import os
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
# import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini client
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY not found in environment variables. Generation will fail.")
    # Optionally raise an error or exit if the key is critical
    # raise ValueError("GEMINI_API_KEY is not set in the environment.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info("Gemini API configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        # Handle configuration error appropriately

# Constants (consider moving to a central config.py)
DEFAULT_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
DEFAULT_QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DEFAULT_COLLECTION_NAME = "io_net_docs_json" # Updated default collection name
DEFAULT_GEMINI_MODEL = "gemini-pro" # Or another suitable model like 'gemini-1.5-flash'

class RagAssistant:
    def __init__(self,
                 embedding_model_name: str = DEFAULT_MODEL_NAME,
                 qdrant_url: str = DEFAULT_QDRANT_URL,
                 collection_name: str = DEFAULT_COLLECTION_NAME,
                 llm_model_name: str = DEFAULT_GEMINI_MODEL):
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
            # Decide how to handle failure: raise error, use fallback, or disable functionality

        try:
            logging.info(f"Connecting to Qdrant at {self.qdrant_url}")
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            # Optional: Check connection or collection existence here
            self.qdrant_client.get_collection(collection_name=self.collection_name) # Check if collection exists
            logging.info(f"Connected to Qdrant and collection '{self.collection_name}' found.")
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant or find collection '{self.collection_name}': {e}")
            # Decide how to handle failure

        if GEMINI_API_KEY: # Only initialize if API key is present
            try:
                logging.info(f"Initializing LLM: {self.llm_model_name}")
                self.llm = genai.GenerativeModel(self.llm_model_name)
                logging.info("LLM initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize LLM '{self.llm_model_name}': {e}")
        else:
            logging.warning("LLM not initialized due to missing GEMINI_API_KEY.")


    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant context from Qdrant based on the query.
        Returns a list of search results (hits).
        """
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
                with_payload=True # Ensure payload is returned
            )
            logging.info(f"Retrieved {len(search_result)} context chunks from Qdrant.")
            # Return the list of Hit objects directly
            return search_result
        except Exception as e:
            logging.error(f"Error during Qdrant search: {e}")
            return []

    def generate(self, query: str, search_results: List[Any]) -> str:
        """
        Generates an answer using the LLM based on the query and retrieved context.
        """
        if not self.llm:
            logging.error("Cannot generate: LLM not initialized.")
            return {"answer": "Error: LLM is not available.", "sources": []} # Return dict
        if not search_results:
             # Return dict structure even if no results
             return {"answer": "Sorry, I couldn't find relevant information in the documents to answer your question.", "sources": []}

        logging.info("Generating answer using LLM...")
        # Extract context text and also prepare source metadata
        context_texts = []
        sources_metadata = []
        for hit in search_results:
            if hit.payload:
                if 'text' in hit.payload:
                    context_texts.append(hit.payload['text'])
                # Collect source info even if text is missing for some reason
                sources_metadata.append({
                    "score": hit.score, # Include relevance score
                    "source_url": hit.payload.get("source_url"),
                    "image_urls": hit.payload.get("image_urls", []),
                    "link_urls": hit.payload.get("link_urls", []),
                    "source_file": hit.payload.get("source_file"), # Keep for debugging/reference
                    # "text_chunk": hit.payload.get("text") # Optionally include the chunk text
                })

        if not context_texts:
             logging.warning("No text found in Qdrant search result payloads.")
             # Return dict structure
             return {"answer": "Sorry, I found some documents but couldn't extract text to form an answer.", "sources": sources_metadata}

        # Construct prompt
        prompt = f"""Based ONLY on the following context extracted from the io.net documentation, answer the user's question.
If the context does not contain the answer, state that you cannot answer based on the provided information. Do not make up information.

Context:
---
{chr(10).join(f"- {ctx}" for ctx in context_texts)}
---

User Question: {query}

Answer:""" # Use newline instead of backslash n

        try:
            # Note: Check Gemini API documentation for specific parameters (e.g., safety settings, temperature)
            response = self.llm.generate_content(prompt)
            answer_text = response.text
            logging.info("Answer generated successfully.")
            # Return dict with answer and sources
            return {"answer": answer_text, "sources": sources_metadata}
        except Exception as e:
            logging.error(f"Error during LLM generation: {e}")
            # Return dict structure on error
            return {"answer": "Error: Failed to generate answer from LLM.", "sources": sources_metadata} # Include sources found so far


    def answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answers a query using the full RAG pipeline (retrieve then generate).
        Returns a dictionary containing the answer text and source information.
        """
        search_results = self.retrieve(query, top_k=top_k)
        # The generate function now returns the dictionary directly
        result = self.generate(query, search_results)
        return result

if __name__ == "__main__":
    logging.info("--- Running RAG Core Standalone Test ---")
    # This requires Qdrant to be running and the collection to be populated.
    # Also requires .env file with GEMINI_API_KEY

    try:
        assistant = RagAssistant()
        if assistant.embedding_model and assistant.qdrant_client and assistant.llm:
            test_query = "What is io.net?" # Example query
            logging.info(f"Testing with query: '{test_query}'")
            result = assistant.answer(test_query)
            print("-" * 20)
            print(f"Query: {test_query}")
            print(f"Response:\n{result.get('answer')}")
            print(f"Sources Found: {len(result.get('sources', []))}")
            if result.get('sources'):
                print(f"  Top Source URL: {result['sources'][0].get('source_url')}")
                print(f"  Top Source Score: {result['sources'][0].get('score')}")
            print("-" * 20)

            test_query_2 = "How does staking work?"
            logging.info(f"Testing with query: '{test_query_2}'")
            result_2 = assistant.answer(test_query_2)
            print(f"Query: {test_query_2}")
            print(f"Response:\n{result_2.get('answer')}")
            print(f"Sources Found: {len(result_2.get('sources', []))}")
            if result_2.get('sources'):
                print(f"  Top Source URL: {result_2['sources'][0].get('source_url')}")
                print(f"  Top Source Score: {result_2['sources'][0].get('score')}")
            print("-" * 20)
        else:
            logging.error("RAG Assistant components not fully initialized. Cannot run test.")

    except Exception as e:
        logging.error(f"Error during standalone test: {e}")

    logging.info("--- RAG Core Standalone Test Finished ---")
