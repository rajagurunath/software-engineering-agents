from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
import logging
from typing import List, Dict, Any
from core.observability import get_opik_handler
# Assuming these are available or can be configured
DEFAULT_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
DEFAULT_QDRANT_URL = "http://localhost:6333" # Or load from environment/config
DEFAULT_COLLECTION_NAME = "io_net_docs_json4" # The new collection for JSON data
DEFAULT_GEMINI_MODEL = "gemini-pro" # Or another suitable model

class RagAssistant:
    def __init__(self,
                 embedding_model_name: str = DEFAULT_MODEL_NAME,
                 qdrant_url: str = DEFAULT_QDRANT_URL,
                 collection_name: str = DEFAULT_COLLECTION_NAME,
                 llm_model_name: str = 'Qwen/Qwen3-235B-A22B-FP8',
                 openai_api_key: str = None,
                 openai_base_url: str = 'https://api.intelligence.io.solutions/api/v1'):
        logging.info("Initializing RAG Assistant...")
        self.embedding_model_name = embedding_model_name
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.llm_model_name = llm_model_name

        self.embedding_model = None
        self.qdrant_client = None
        self.llm = None

        self._initialize_components()

    def _initialize_components(self):
        """Initializes the embedding model, Qdrant client, and LLM."""
        try:
            logging.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logging.info("Embedding model loaded.")
        except Exception as e:
            logging.error(f"Failed to load embedding model '{self.embedding_model_name}': {e}")

        try:
            logging.info(f"Connecting to Qdrant at {self.qdrant_url}")
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            # Check connection implicitly by trying an operation
            self.qdrant_client.get_collections() 
            logging.info("Successfully connected to Qdrant.")
        except Exception as e:
            logging.error(f"Failed to connect or communicate with Qdrant at {self.qdrant_url}: {e}")
        # openai_api_key ='io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6Ijk1Y2U5MzYxLTQ0N2YtNGVjMC1hNjk4LTc2NGMyYTJkMTViOSIsImV4cCI6NDkwMzM1MDAyNX0.cZQbciVwEHZTNu9NclK8uNPo0b_KeliX5-xgc552AhafaLrvjTedcNUePHNn7mXKmt_LENv5o5VqsHP4EMdtnA'
        # openai_api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6Ijk1Y2U5MzYxLTQ0N2YtNGVjMC1hNjk4LTc2NGMyYTJkMTViOSIsImV4cCI6NDkwMzM0OTYwOX0.FT92Mlf4b-ywGHWl09ecZVowTyCEe9t_dPcgCUAOmYptndQel9XtqvAnCIBvqmvchcf1Qt3obi-jEJ8YoF9KZQ"
        openai_api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6Ijk1Y2U5MzYxLTQ0N2YtNGVjMC1hNjk4LTc2NGMyYTJkMTViOSIsImV4cCI6NDkwNTM5NTI1M30.pmUWludt_XHE7FNEOnu90nNdsvmmhvuizcq0ny6zShWljfFLzCLYBdCJBCRW8YppGHl3NZvR_1Y3xhqh6g_RqQ"
        if openai_api_key:
            try:
                logging.info(f"Initializing LLM: {self.llm_model_name}")
                self.llm = ChatOpenAI(
                    default_headers= {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                                            "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Referer": "https://io.solutions/",
                                "Connection": "keep-alive"
                            },
                    model='Qwen/Qwen3-235B-A22B-FP8',
                    max_retries=2,
                    # model='meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8',
                    api_key=openai_api_key,
                    base_url='https://api.intelligence.io.solutions/api/v1',
                    callbacks=[get_opik_handler()],
                    timeout=600,
                )
                logging.info("LLM initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize LLM '{self.llm_model_name}': {e}")
        else:
            logging.warning("LLM not initialized due to missing OPENAI_API_KEY.")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.embedding_model or not self.qdrant_client:
            logging.error("Cannot retrieve: Embedding model or Qdrant client not initialized.")
            return []

        logging.info(f"Retrieving context for query (first 50 chars): '{query[:50]}...'")
        try:
            query_vector = self.embedding_model.encode(query).tolist()

            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True
            )
            logging.info(f"Retrieved {len(search_result)} context chunks from Qdrant.")
            return search_result
        except Exception as e:
            logging.error(f"Error during Qdrant search: {e}")
            return []

    def generate(self, query: str, search_results: List[Any]) -> Dict[str, Any]:
        if not self.llm:
            logging.error("Cannot generate: LLM not initialized.")
            return {"answer": "Error: LLM is not available.", "sources": []}
        if not search_results:
             return {"answer": "Sorry, I couldn't find relevant information in the documents to answer your question.", "sources": []}

        logging.info("Generating answer using LLM...")
        context_texts = []
        sources_metadata = []
        for hit in search_results:
            if hit.payload:
                if 'text' in hit.payload:
                    context_texts.append(hit.payload['text'])
                sources_metadata.append({
                    "score": hit.score,
                    "text": hit.payload.get("text"),
                    "source_url": hit.payload.get("source_url"),
                    "image_urls": hit.payload.get("image_urls", []),
                    "link_urls": hit.payload.get("link_urls", []),
                    "source_file": hit.payload.get("source_file"),
                })

        if not context_texts:
             logging.warning("No text found in Qdrant search result payloads.")
             return {"answer": "Sorry, I found some documents but couldn't extract text to form an answer.", "sources": sources_metadata}

        prompt = f"""Based ONLY on the following context extracted from the io.net documentation, answer the user's query.
If the context does not contain the answer, state that you cannot answer based on the provided information. Do not make up information.

And make sure you provide the answer in a concise and clear manner and greet the user in a friendly way if demanded by user question.
Context:
---
{chr(10).join(f"- {ctx}" for ctx in context_texts[:1])}
---

User Question: {query}

Answer:"""

        try:
            # Assuming ChatOpenAI has an invoke or similar method
            response = self.llm.invoke(prompt)
            answer_text = response.content # Might need adjustment based on actual response structure
            logging.info("Answer generated successfully.")
            link_sorting_prompt = f"""
                    you are a helpful assistant. who can sort the helpful or relevant links based on the question asked and answer provided to the question by LLM Model
                    Dont speech anything, just return the sorted links in a list format separated by new line
                    Question: {query}
                    Answer: {answer_text}
                    Links: {chr(10).join(f"- {link}" for link in sources_metadata[0].get("link_urls", []))}
                    link sorting:
                """
            response = self.llm.invoke(link_sorting_prompt)
            sorted_links = response.content.split("\n")
            followup_questions_prompt = f"""
                    you are a helpful assistant. who can generate followup questions based on the question asked and answer provided to the question by LLM Model
                    Dont speech anything, just return the followup questions in a list format separated by new line
                    Question: {query}
                    Answer: {answer_text}
                    Followup questions:
                """
            response = self.llm.invoke(followup_questions_prompt)
            followup_questions = response.content.split("\n")
            return {"answer": answer_text, "sources": sources_metadata, 
                    "relevant_source_links": sorted_links,
                    "followup_questions": followup_questions}
        except Exception as e:
            logging.error(f"Error during LLM generation: {e}")
            return {"answer": "Error: Failed to generate answer from LLM.", "sources": sources_metadata,"relevant_source_links": []}

    def answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        # Use LLM to determine if the query is a greeting
        try:
            intent_check_prompt = f"""
            You are a helpful assistant. Determine if the following query is a greeting.
            Respond with "greeting" if it is a greeting, otherwise respond with "other".
            Query: {query}
            Intent:
            """
            response = self.llm.invoke(intent_check_prompt)
            intent = response.content.strip().lower()
        except Exception as e:
            logging.error(f"Error during LLM intent check: {e}")
            intent = "other"

        if intent == "greeting":
            greeting_response_prompt = f"""
            You are a friendly assistant. Generate a warm and concise greeting response to the user's query.
            Query: {query}
            Greeting Response:
            """
            try:
                greeting_response = self.llm.invoke(greeting_response_prompt)
                return {"answer": greeting_response.content.strip(), "sources": [], "relevant_source_links": [], "followup_questions": []}
            except Exception as e:
                logging.error(f"Error during LLM greeting response generation: {e}")
                return {"answer": "Hello! What can I help you with today?", "sources": [], "relevant_source_links": [], "followup_questions": []}
        
        # Perform RAG if the query is not a greeting
        search_results = self.retrieve(query, top_k=top_k)
        result = self.generate(query, search_results)
        return result
