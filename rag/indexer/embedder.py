import os
import logging
import markdown
import json # Added import
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from nltk.tokenize import sent_tokenize

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default model name (can be configured)
DEFAULT_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
# Directory for markdown files (kept for potential backward compatibility or other uses)
DEFAULT_MARKDOWN_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown4')
# Directory for JSON files (NEW)
DEFAULT_JSON_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown4')

# Simple chunking parameters
CHUNK_SIZE = 500 # Approximate characters per chunk
CHUNK_OVERLAP = 50 # Characters overlap between chunks

def extract_text_from_html(html_content: str) -> str:
    """Converts HTML content to plain text."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        # Get text, normalize whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        logging.error(f"Error converting HTML to text: {e}")
        return "" # Return empty string on error

def markdown_to_text(md_content: str) -> str:
    """Converts markdown content to plain text."""
    try:
        html = markdown.markdown(md_content)
        return extract_text_from_html(html) # Reuse HTML extraction
    except Exception as e:
        logging.error(f"Error converting markdown to text: {e}")
        return "" # Return empty string on error

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Improved text chunking method for RAG applications.
    Splits text into chunks based on sentences while maintaining chunk size and overlap constraints.
    """
    if not text:
        return []


    # Tokenize text into sentences
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        # If adding the sentence exceeds the chunk size, finalize the current chunk
        if current_length + sentence_length > chunk_size:
            chunks.append(" ".join(current_chunk))
            # Start a new chunk with overlap
            overlap = " ".join(current_chunk[-chunk_overlap:]) if chunk_overlap > 0 else ""
            current_chunk = [overlap] if overlap else []
            current_length = len(overlap)

        # Add the sentence to the current chunk
        current_chunk.append(sentence)
        current_length += sentence_length

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Filter out empty chunks
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def load_process_embed_json(json_dir: str = DEFAULT_JSON_DIR, model_name: str = DEFAULT_MODEL_NAME) -> List[Dict[str, Any]]:
    """
    Loads JSON files from crawl4ai, extracts text and metadata, chunks text,
    generates embeddings, and returns structured data.
    """
    processed_data = []
    chunks_metadata = [] # Store metadata per chunk before embedding

    logging.info(f"Loading and processing JSON files from: {json_dir}")
    if not os.path.isdir(json_dir):
        logging.error(f"JSON directory not found: {json_dir}")
        return []

    for i,filename in enumerate(os.listdir(json_dir)):
        if filename.lower().endswith(".md"):
            file_path = os.path.join(json_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                plain_text = f.read()
            
            # Convert markdown to plain text
            # plain_text = markdown_to_text(md_content)
            
            # Remove links and keep only paragraph texts
            plain_text = "\n".join([line for line in plain_text.splitlines() if not line.startswith("[](") and line.strip()])
            plain_text = "\n".join([line for line in plain_text.splitlines() if not line.startswith("![](") and line.strip()])
            plain_text = "\n".join([line for line in plain_text.splitlines() if not line.startswith("* [") and line.strip()])
        if filename.lower().endswith(".json"):
            file_path = os.path.join(json_dir, filename)
            logging.debug(f"Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # # Extract text content (prioritize cleaned_html, fallback to html)
                # plain_text = ""
                # # if data.get('cleaned_html'):
                # #     # Assuming cleaned_html is already plain text or needs minimal cleaning
                # #     # If it's HTML, we might need BeautifulSoup again
                # #     # For now, assume it's usable text
                # #     plain_text = data['cleaned_html'] # Or apply minimal cleaning if needed
                # if data.get('html'):
                #     logging.debug(f"Using 'html' field for text extraction from {filename}")
                #     plain_text = extract_text_from_html(data['html'])
                # else:
                #     logging.warning(f"No 'cleaned_html' or 'html' field found in {filename}. Skipping text extraction.")
                #     # Decide if you want to skip the file entirely or proceed with metadata only
                #     # continue # Option: skip file if no text

                # if not plain_text:
                #     logging.warning(f"No text could be extracted from {filename}. Skipping file.")
                #     continue

                # Extract metadata
                source_url = data.get('url', None)
                image_urls = [img.get('src') for img in data.get('media', {}).get('images', []) if img.get('src')]
                internal_links = [link.get('href') for link in data.get('links', {}).get('internal', []) if link.get('href')]
                external_links = [link.get('href') for link in data.get('links', {}).get('external', []) if link.get('href')]
                link_urls = internal_links + external_links

                # Chunk the text
                # chunks = chunk_text(plain_text)
                # for i, chunk in enumerate(chunks):
                # Store chunk text and its associated metadata
                chunks_metadata.append({
                    "text": plain_text,
                    "source_file": file_path,
                    "chunk_index": i,
                    "source_url": source_url,
                    "image_urls": image_urls,
                    "link_urls": link_urls
                })

            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from file {filename}")
            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}", exc_info=True)

    # if not chunks_metadata:
    #     logging.warning("No text chunks found to embed.")
    #     return []

    logging.info(f"Found {len(chunks_metadata)} text chunks to embed.")
    logging.info(f"Loading embedding model: {model_name}")
    try:
        # Separate texts for batch embedding
        texts_to_embed = [item['text'] for item in chunks_metadata]

        model = SentenceTransformer(model_name)
        logging.info("Generating embeddings...")
        embeddings = model.encode(texts_to_embed, show_progress_bar=True)
        logging.info("Embeddings generated successfully.")

        # Combine metadata with embeddings
        for i, item in enumerate(chunks_metadata):
            processed_data.append({
                "text": item['text'],
                "source_file": item['source_file'],
                "source_url": item['source_url'],
                "image_urls": item['image_urls'],
                "link_urls": item['link_urls'],
                "embedding": embeddings[i].tolist() # Convert numpy array to list
            })

    except Exception as e:
        logging.error(f"Error during embedding generation: {e}", exc_info=True)
        return [] # Return empty list on embedding error

    logging.info(f"Successfully processed and embedded {len(processed_data)} chunks.")
    return processed_data


# --- Keep the old markdown function for potential compatibility ---
def load_process_and_embed(markdown_dir: str = DEFAULT_MARKDOWN_DIR, model_name: str = DEFAULT_MODEL_NAME) -> List[Dict[str, Any]]:
    """
    Loads markdown files, extracts text, chunks it, generates embeddings,
    and returns a list of dictionaries containing text, source, and embedding.
    (LEGACY - Use load_process_embed_json for new JSON data)
    """
    processed_data = []
    texts_to_embed = []
    sources = []

    logging.info(f"[LEGACY] Loading and processing markdown files from: {markdown_dir}")
    if not os.path.isdir(markdown_dir):
        logging.error(f"[LEGACY] Markdown directory not found: {markdown_dir}")
        return []

    for filename in os.listdir(markdown_dir):
        if filename.lower().endswith(".md"):
            file_path = os.path.join(markdown_dir, filename)
            logging.debug(f"[LEGACY] Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                plain_text = markdown_to_text(md_content)
                if not plain_text:
                    logging.warning(f"[LEGACY] No text extracted from {filename}")
                    continue

                chunks = chunk_text(plain_text)
                for i, chunk in enumerate(chunks):
                    texts_to_embed.append(chunk)
                    sources.append({"source_file": file_path, "chunk_index": i})

            except Exception as e:
                logging.error(f"[LEGACY] Error processing file {filename}: {e}")

    if not texts_to_embed:
        logging.warning("[LEGACY] No text chunks found to embed.")
        return []

    logging.info(f"[LEGACY] Found {len(texts_to_embed)} text chunks to embed.")
    logging.info(f"[LEGACY] Loading embedding model: {model_name}")
    try:
        model = SentenceTransformer(model_name)
        logging.info("[LEGACY] Generating embeddings...")
        embeddings = model.encode(texts_to_embed, show_progress_bar=True)
        logging.info("[LEGACY] Embeddings generated successfully.")

        for i, text in enumerate(texts_to_embed):
            processed_data.append({
                "text": text,
                "source": sources[i]['source_file'], # Keep original 'source' key for legacy compatibility
                "embedding": embeddings[i].tolist()
            })

    except Exception as e:
        logging.error(f"[LEGACY] Error during embedding generation: {e}")
        return []

    logging.info(f"[LEGACY] Successfully processed and embedded {len(processed_data)} chunks.")
    return processed_data


if __name__ == "__main__":
    logging.info("--- Running Embedder Standalone ---")

    # Example: Test the new JSON function
    logging.info("Testing JSON embedding function...")
    if not os.path.exists(DEFAULT_JSON_DIR):
         logging.warning(f"JSON directory '{DEFAULT_JSON_DIR}' not found.")
         logging.warning("Please ensure JSON files exist (e.g., from crawl4ai).")
    else:
        embedded_json_chunks = load_process_embed_json()
        if embedded_json_chunks:
            logging.info(f"Example embedded JSON chunk data structure:")
            logging.info(f"Total JSON chunks: {len(embedded_json_chunks)}")
            if embedded_json_chunks:
                 first_chunk = embedded_json_chunks[0]
                 logging.info(f"  Text (first 50 chars): {first_chunk.get('text', '')[:50]}...")
                 logging.info(f"  Source File: {first_chunk.get('source_file', 'N/A')}")
                 logging.info(f"  Source URL: {first_chunk.get('source_url', 'N/A')}")
                 logging.info(f"  Image URLs count: {len(first_chunk.get('image_urls', []))}")
                 logging.info(f"  Link URLs count: {len(first_chunk.get('link_urls', []))}")
                 logging.info(f"  Embedding vector length: {len(first_chunk.get('embedding', []))}")
        else:
            logging.warning("No JSON chunks were embedded.")

    # Keep the old markdown test code commented out or remove if no longer needed
    # logging.info("\nTesting legacy Markdown embedding function...")
    # if not os.path.exists(DEFAULT_MARKDOWN_DIR):
    #      logging.warning(f"Markdown directory '{DEFAULT_MARKDOWN_DIR}' not found.")
    # else:
    #     embedded_md_chunks = load_process_and_embed()
    #     # ... (rest of the markdown test code) ...

    logging.info("--- Embedder Standalone Finished ---")
