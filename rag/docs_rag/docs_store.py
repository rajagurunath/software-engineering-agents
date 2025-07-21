import logging
from typing import List, Dict, Any, Optional, Literal
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from config.settings import settings
from core.observability import get_opik_handler
import requests
import json

logger = logging.getLogger(__name__)

class RagAssistant:
    """
    RAG Assistant that can use either Qdrant or R2R for document retrieval.
    Supports switching between backends without changing the interface.
    """
    
    def __init__(
        self,
        retrieval_backend: Literal["qdrant", "r2r"] = "qdrant",
        embedding_model_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        llm_model_name: Optional[str] = None,
        top_k: int = 5
    ):
        """
        Initialize RAG Assistant with configurable backend.
        
        Args:
            retrieval_backend: Either "qdrant" or "r2r"
            embedding_model_name: Override default embedding model
            collection_name: Override default collection name
            llm_model_name: Override default LLM model
            top_k: Default number of results to retrieve
        """
        logger.info(f"Initializing RAG Assistant with {retrieval_backend} backend...")
        
        # Configuration from settings with fallbacks
        self.retrieval_backend = retrieval_backend
        self.embedding_model_name = embedding_model_name or settings.qdrant_embedding_model_name
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.llm_model_name = llm_model_name or settings.io_model
        self.top_k = top_k
        
        # Backend-specific configurations
        self.qdrant_url = settings.qdrant_url
        self.r2r_base_url = settings.rag_base_url
        self.r2r_api_key = settings.iointelligence_api_key
        
        # Initialize components
        self.embedding_model = None
        self.qdrant_client = None
        self.llm = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding model, retrieval backend, and LLM."""
        self._initialize_embedding_model()
        self._initialize_retrieval_backend()
        self._initialize_llm()
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model (only needed for Qdrant)."""
        if self.retrieval_backend == "qdrant":
            try:
                logger.info(f"Loading embedding model: {self.embedding_model_name}")
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load embedding model '{self.embedding_model_name}': {e}")
                raise
    
    def _initialize_retrieval_backend(self):
        """Initialize the selected retrieval backend."""
        if self.retrieval_backend == "qdrant":
            self._initialize_qdrant()
        elif self.retrieval_backend == "r2r":
            self._initialize_r2r()
        else:
            raise ValueError(f"Unsupported retrieval backend: {self.retrieval_backend}")
    
    def _initialize_qdrant(self):
        """Initialize Qdrant client."""
        try:
            logger.info(f"Connecting to Qdrant at {self.qdrant_url}")
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            # Test connection
            self.qdrant_client.get_collections()
            logger.info(f"Successfully connected to Qdrant collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant at {self.qdrant_url}: {e}")
            raise
    
    def _initialize_r2r(self):
        """Initialize R2R client configuration."""
        if not self.r2r_api_key:
            raise ValueError("R2R API key is required but not found in settings")
        
        self.r2r_headers = {
            "Authorization": f"Bearer {self.r2r_api_key}",
            "Content-Type": "application/json"
        }
        
        # Test R2R connection
        try:
            response = requests.get(
                f"{self.r2r_base_url}/collections",
                headers=self.r2r_headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully connected to R2R API.")
        except Exception as e:
            logger.error(f"Failed to connect to R2R at {self.r2r_base_url}: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize the LLM."""
        try:
            logger.info(f"Initializing LLM: {self.llm_model_name}")
            self.llm = ChatOpenAI(
                model=self.llm_model_name,
                api_key=settings.iointelligence_api_key,
                base_url=settings.openai_base_url,
                # callbacks=[get_opik_handler()],
                timeout=600,
                max_retries=2,
                default_headers={
                    "User-Agent": "io.net RAG Assistant",
                    "Accept": "application/json",
                    "Connection": "keep-alive"
                }
            )
            logger.info("LLM initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM '{self.llm_model_name}': {e}")
            raise
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents using the configured backend.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve (uses instance default if None)
            
        Returns:
            List of search results with metadata
        """
        top_k = top_k or self.top_k
        
        if self.retrieval_backend == "qdrant":
            return self._retrieve_qdrant(query, top_k)
        elif self.retrieval_backend == "r2r":
            return self._retrieve_r2r(query, top_k)
        else:
            raise ValueError(f"Unsupported retrieval backend: {self.retrieval_backend}")
    
    def _retrieve_qdrant(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve documents using Qdrant."""
        if not self.embedding_model or not self.qdrant_client:
            logger.error("Qdrant components not initialized.")
            return []
        
        logger.info(f"Retrieving from Qdrant: '{query[:50]}...'")
        try:
            query_vector = self.embedding_model.encode(query).tolist()
            
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True
            )
            
            logger.info(f"Retrieved {len(search_result)} results from Qdrant.")
            logger.debug(f"Qdrant search results: {search_result}")
            
            # Normalize Qdrant results to common format
            normalized_results = []
            for hit in search_result:
                normalized_results.append({
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "source_url": hit.payload.get("source_url"),
                    "image_urls": hit.payload.get("image_urls", []),
                    "link_urls": hit.payload.get("link_urls", []),
                    "source_file": hit.payload.get("source_file"),
                    "metadata": hit.payload
                })
            
            logger.debug(f"Normalized results: {normalized_results}")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Error during Qdrant search: {e}", exc_info=True)
            return []
    
    def _retrieve_r2r(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve documents using R2R API."""
        logger.info(f"Retrieving from R2R: '{query[:50]}...'")
        try:
            search_payload = {
                "query": query,
                "search_settings": {
                    "use_semantic_search": True,
                    "use_fulltext_search": True,
                    "limit": top_k,
                    "include_metadatas": True,
                    "include_scores": True
                }
            }
            
            response = requests.post(
                f"{self.r2r_base_url}/retrieval/search",
                headers=self.r2r_headers,
                json=search_payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", {}).get("chunk_search_results", [])
            
            logger.info(f"Retrieved {len(results)} results from R2R.")
            
            # Normalize R2R results to common format
            normalized_results = []
            for result in results:
                metadata = result.get("metadata", {})
                normalized_results.append({
                    "score": result.get("score", 0.0),
                    "text": result.get("text", ""),
                    "source_url": metadata.get("source_url"),
                    "image_urls": metadata.get("image_urls", []),
                    "link_urls": metadata.get("link_urls", []),
                    "source_file": metadata.get("source_file"),
                    "metadata": metadata
                })
            
            return normalized_results
            
        except Exception as e:
            logger.error(f"Error during R2R search: {e}")
            return []
    
    def generate(self, query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer using LLM based on retrieved context.
        
        Args:
            query: User query
            search_results: Retrieved documents
            
        Returns:
            Dictionary with answer, sources, and additional metadata
        """
        if not self.llm:
            logger.error("LLM not initialized.")
            return {
                "answer": "Error: LLM is not available.",
                "sources": [],
                "relevant_source_links": [],
                "followup_questions": []
            }
        
        if not search_results:
            return {
                "answer": "Sorry, I couldn't find relevant information in the documents to answer your question.",
                "sources": [],
                "relevant_source_links": [],
                "followup_questions": []
            }
        
        logger.info("Generating answer using LLM...")
        
        # Extract context and prepare sources
        context_texts = []
        sources_metadata = []
        
        for result in search_results:
            if result.get("text"):
                context_texts.append(result["text"])
            sources_metadata.append(result)
        
        if not context_texts:
            logger.warning("No text found in search results.")
            return {
                "answer": "Sorry, I found some documents but couldn't extract text to form an answer.",
                "sources": sources_metadata,
                "relevant_source_links": [],
                "followup_questions": []
            }
        
        # Generate main answer
        main_prompt = f"""Based ONLY on the following context extracted from the io.net documentation, answer the user's query.
If the context does not contain the answer, state that you cannot answer based on the provided information. Do not make up information.

Provide a concise and clear answer. If the user's query is a greeting, respond in a friendly manner.

Context:
---
{chr(10).join(f"- {ctx}" for ctx in context_texts[:3])}
---

User Question: {query}

Answer:"""
        
        try:
            response = self.llm.invoke(main_prompt)
            answer_text = response.content.strip()
            logger.info("Answer generated successfully.")
            
            # Generate relevant links
            relevant_links = self._generate_relevant_links(query, answer_text, sources_metadata)
            
            # Generate followup questions
            followup_questions = self._generate_followup_questions(query, answer_text)
            
            return {
                "answer": answer_text,
                "sources": sources_metadata,
                "relevant_source_links": relevant_links,
                "followup_questions": followup_questions
            }
            
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}")
            return {
                "answer": "Error: Failed to generate answer from LLM.",
                "sources": sources_metadata,
                "relevant_source_links": [],
                "followup_questions": []
            }
    
    def _generate_relevant_links(self, query: str, answer: str, sources: List[Dict]) -> List[str]:
        """Generate sorted relevant links based on query and answer."""
        try:
            # Collect all unique links from sources
            all_links = set()
            for source in sources:
                link_urls = source.get("link_urls", [])
                if isinstance(link_urls, list):
                    all_links.update(link_urls)
            
            if not all_links:
                return []
            
            link_sorting_prompt = f"""You are a helpful assistant. Sort the most relevant links based on the question and answer.
Return only the sorted links, one per line, without any additional text.

Question: {query}
Answer: {answer}
Links: {chr(10).join(all_links)}

Sorted relevant links:"""
            
            response = self.llm.invoke(link_sorting_prompt)
            sorted_links = [link.strip() for link in response.content.split("\n") if link.strip()]
            return sorted_links[:5]  # Return top 5 relevant links
            
        except Exception as e:
            logger.error(f"Error generating relevant links: {e}")
            return []
    
    def _generate_followup_questions(self, query: str, answer: str) -> List[str]:
        """Generate followup questions based on query and answer."""
        try:
            followup_prompt = f"""You are a helpful assistant. Generate 3-5 relevant followup questions based on the question and answer.
Return only the questions, one per line, without any additional text.

Question: {query}
Answer: {answer}

Followup questions:"""
            
            response = self.llm.invoke(followup_prompt)
            questions = [q.strip() for q in response.content.split("\n") if q.strip()]
            return questions[:5]  # Return up to 5 questions
            
        except Exception as e:
            logger.error(f"Error generating followup questions: {e}")
            return []
    
    def _is_greeting(self, query: str) -> bool:
        """Determine if the query is a greeting."""
        try:
            intent_prompt = f"""Determine if the following query is a greeting.
Respond with only "greeting" or "other".

Query: {query}
Intent:"""
            
            response = self.llm.invoke(intent_prompt)
            intent = response.content.strip().lower()
            return intent == "greeting"
            
        except Exception as e:
            logger.error(f"Error during intent classification: {e}")
            return False
    
    def _generate_greeting_response(self, query: str) -> str:
        """Generate a friendly greeting response."""
        try:
            greeting_prompt = f"""Generate a warm and concise greeting response to the user's query.

Query: {query}
Greeting Response:"""
            
            response = self.llm.invoke(greeting_prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting response: {e}")
            return "Hello! How can I help you with io.net today?"
    
    def answer(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Answer a query using the full RAG pipeline.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve (uses instance default if None)
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Check if query is a greeting
        if self._is_greeting(query):
            greeting_response = self._generate_greeting_response(query)
            return {
                "answer": greeting_response,
                "sources": [],
                "relevant_source_links": [],
                "followup_questions": []
            }
        
        # Perform RAG pipeline
        search_results = self.retrieve(query, top_k)
        result = self.generate(query, search_results)
        return result
    
    def switch_backend(self, new_backend: Literal["qdrant", "r2r"]):
        """
        Switch retrieval backend at runtime.
        
        Args:
            new_backend: Either "qdrant" or "r2r"
        """
        if new_backend == self.retrieval_backend:
            logger.info(f"Already using {new_backend} backend.")
            return
        
        logger.info(f"Switching from {self.retrieval_backend} to {new_backend} backend...")
        self.retrieval_backend = new_backend
        
        # Reinitialize components for new backend
        if new_backend == "qdrant":
            self._initialize_embedding_model()
            self._initialize_qdrant()
        elif new_backend == "r2r":
            self._initialize_r2r()
        else:
            raise ValueError(f"Unsupported backend: {new_backend}")
        
        logger.info(f"Successfully switched to {new_backend} backend.")


def create_rag_assistant(
    backend: Literal["qdrant", "r2r"] = "qdrant",
    **kwargs
) -> RagAssistant:
    """
    Factory function to create a RAG assistant with the specified backend.
    
    Args:
        backend: Retrieval backend to use
        **kwargs: Additional configuration options
        
    Returns:
        Configured RagAssistant instance
    """
    return RagAssistant(retrieval_backend=backend, **kwargs)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create RAG assistant with Qdrant backend
    rag = create_rag_assistant(backend="qdrant")
    
    # Test query
    result = rag.answer("What is io.net?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])}")
    
    # Switch to R2R backend if needed
    # rag.switch_backend("r2r")
    # result = rag.answer("How does staking work?")
