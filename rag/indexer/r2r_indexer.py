import os
import logging
import json
import subprocess
import tempfile
import uuid
from typing import List, Dict, Any
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# R2R Configuration
R2R_API_BASE_URL = settings.r2r_api_base_url
# It's crucial to set this environment variable with your actual API key
R2R_API_KEY = os.getenv("IOINTELLIGENCE_API_KEY")
COLLECTION_NAME = "io_net_docs_r2r"
COLLECTION_DESCRIPTION = "Collection for io.net documentation indexed via R2R API"

# Data source directory
DEFAULT_JSON_DIR = os.path.join(os.path.dirname(__file__), '..','..', 'data', 'markdown')

def run_curl_command(command: list) -> (bool, dict):
    """Executes a curl command and returns success status and JSON response."""
    logging.debug(f"Executing command: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.debug(f"Curl command stdout: {process.stdout}")
        if process.stdout:
            return True, json.loads(process.stdout)
        return True, {}
    except subprocess.CalledProcessError as e:
        logging.error(f"Curl command failed with exit code {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        return False, {"error": e.stderr}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from curl output: {e}")
        logging.error(f"Raw output: {process.stdout}")
        return False, {"error": "Invalid JSON response"}
    except Exception as e:
        logging.error(f"An unexpected error occurred while running curl: {e}")
        return False, {"error": str(e)}

def get_collection_id(collection_name: str) -> str or None:
    """Gets the ID of a collection by its name."""
    if not R2R_API_KEY:
        logging.error("IOINTELLIGENCE_API_KEY environment variable not set.")
        return None

    command = [
        "curl", "-X", "GET",
        f"{R2R_API_BASE_URL}/collections",
        "-H", f"Authorization: Bearer {R2R_API_KEY}"
    ]
    success, response = run_curl_command(command)
    if success:
        for collection in response.get('results', []):
            if collection.get('name') == collection_name:
                logging.info(f"Found existing collection '{collection_name}' with ID: {collection['id']}")
                return collection['id']
    return None

def create_r2r_collection(collection_name: str, description: str) -> str or None:
    """Creates a new collection in R2R and returns its ID."""
    if not R2R_API_KEY:
        logging.error("IOINTELLIGENCE_API_KEY environment variable not set.")
        return None

    collection_id = get_collection_id(collection_name)
    if collection_id:
        return collection_id

    logging.info(f"Collection '{collection_name}' not found. Creating...")
    command = [
        "curl", "-X", "POST",
        f"{R2R_API_BASE_URL}/collections",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {R2R_API_KEY}",
        "-d", json.dumps({"name": collection_name, "description": description})
    ]
    success, response = run_curl_command(command)
    # Check for the ID within the 'results' object in the response
    if success and response.get('results', {}).get('id'):
        collection_id = response['results']['id']
        logging.info(f"Collection '{collection_name}' created successfully with ID: {collection_id}")
        return collection_id
    else:
        logging.error(f"Failed to create collection '{collection_name}'. Response: {response}")
        return None

def upload_document_to_r2r(file_path: str, metadata: dict, document_id: str = None) -> bool:
    """Uploads a single document file to the R2R API."""
    if not R2R_API_KEY:
        logging.error("IOINTELLIGENCE_API_KEY environment variable not set.")
        return False

    doc_id = document_id or str(uuid.uuid4())
    
    command = [
        "curl", "-X", "POST",
        f"{R2R_API_BASE_URL}/documents",
        "-H", "Content-Type: multipart/form-data",
        "-H", f"Authorization: Bearer {R2R_API_KEY}",
        "-F", f"file=@{file_path};type=text/plain",
        "-F", f"metadata={json.dumps(metadata)}",
        "-F", f"id={doc_id}"
    ]
    
    success, response = run_curl_command(command)
    if success:
        logging.info(f"Successfully uploaded document {doc_id} from file {os.path.basename(file_path)}")
        return True
    else:
        logging.error(f"Failed to upload document from file {os.path.basename(file_path)}. Response: {response}")
        return False

def add_document_to_collection(document_id: str, collection_id: str):
    """Adds an existing document to a collection."""
    if not R2R_API_KEY:
        logging.error("IOINTELLIGENCE_API_KEY environment variable not set.")
        return False
        
    command = [
        "curl", "-X", "POST",
        f"{R2R_API_BASE_URL}/collections/{collection_id}/documents/{document_id}",
        "-H", f"Authorization: Bearer {R2R_API_KEY}",
    ]
    
    success, response = run_curl_command(command)
    if success:
        logging.info(f"Successfully added document {document_id} to collection {collection_id}")
        return True
    else:
        logging.error(f"Failed to add document {document_id} to collection {collection_id}. Response: {response}")
        return False


def process_and_upload_data(json_dir: str, collection_id: str):
    """
    Loads data from JSON files, processes it, and uploads it to R2R.
    """
    logging.info(f"Loading and processing JSON files from: {json_dir}")
    if not os.path.isdir(json_dir):
        logging.error(f"JSON directory not found: {json_dir}")
        return

    files_to_process = [f for f in os.listdir(json_dir) if f.lower().endswith(('.md'))]
    total_files = len(files_to_process)
    logging.info(f"Found {total_files} files to process.")

    for i, filename in enumerate(files_to_process):
        file_path = os.path.join(json_dir, filename)
        logging.info(f"--- Processing file {i+1}/{total_files}: {filename} ---")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if filename.lower().endswith(".md"):
                    content = f.read()
                    # Simple metadata for markdown
                    metadata = {"source_file": filename}
                elif filename.lower().endswith(".json"):
                    data = json.load(f)
                    # Extract text and metadata from JSON
                    content = data.get('text', '') # Assuming text is pre-extracted
                    if not content and data.get('html'):
                         from bs4 import BeautifulSoup
                         soup = BeautifulSoup(data['html'], 'html.parser')
                         content = soup.get_text()

                    metadata = {
                        "source_file": filename,
                        "source_url": data.get('url'),
                        "image_urls": [img.get('src') for img in data.get('media', {}).get('images', []) if img.get('src')],
                        "link_urls": [link.get('href') for link in data.get('links', {}).get('internal', []) if link.get('href')] + [link.get('href') for link in data.get('links', {}).get('external', []) if link.get('href')]
                    }
                    metadata = {k: v for k, v in metadata.items() if v is not None}


            if not content:
                logging.warning(f"No content found in {filename}. Skipping.")
                continue

            # R2R can handle chunking, so we upload the whole document.
            # If we need to chunk manually, that logic would go here.
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding='utf-8') as temp_f:
                temp_f.write(content)
                temp_file_path = temp_f.name

            document_id = str(uuid.uuid4())
            if upload_document_to_r2r(temp_file_path, metadata, document_id):
                add_document_to_collection(document_id, collection_id)

            os.remove(temp_file_path) # Clean up the temporary file

        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}", exc_info=True)


def index_data_to_r2r(json_dir: str = DEFAULT_JSON_DIR, collection_name: str = COLLECTION_NAME):
    """
    Main function to orchestrate indexing data into R2R.
    """
    logging.info(f"--- Starting Data Indexing into R2R (Collection: {collection_name}) ---")

    if not R2R_API_KEY:
        logging.critical("IOINTELLIGENCE_API_KEY environment variable is not set. Aborting.")
        return False

    # 1. Get or create the collection
    collection_id = create_r2r_collection(collection_name, COLLECTION_DESCRIPTION)
    if not collection_id:
        logging.error("Could not obtain collection ID. Aborting indexing.")
        return False

    # 2. Process files and upload them
    process_and_upload_data(json_dir, collection_id)

    logging.info("--- Data Indexing to R2R Finished ---")
    return True


if __name__ == "__main__":
    logging.info("Running R2R indexer directly...")
    if index_data_to_r2r():
        logging.info("R2R indexing process completed successfully.")
    else:
        logging.error("R2R indexing process failed.")
