import os
import logging
import uuid # Added for unique IDs
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
# Import the new JSON processing function and its default directory
from rag.indexer.embedder import load_process_embed_json, DEFAULT_MODEL_NAME, DEFAULT_JSON_DIR
from sentence_transformers import SentenceTransformer # Needed to get vector size

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333") # Allow overriding via env var
COLLECTION_NAME = "io_net_docs" # Consider a new collection name for JSON data

def get_vector_size(model_name: str) -> int:
    """Gets the embedding dimension size for a Sentence Transformer model."""
    try:
        # Load the model just to get the dimension
        temp_model = SentenceTransformer(model_name)
        return temp_model.get_sentence_embedding_dimension()
    except Exception as e:
        logging.error(f"Could not determine vector size for model {model_name}: {e}")
        # Fallback to a common default, but log a warning
        logging.warning("Falling back to default vector size 768. Ensure this matches your model.")
        return 768

def index_data_to_qdrant(
    json_dir: str = DEFAULT_JSON_DIR, # Changed parameter name and default
    model_name: str = DEFAULT_MODEL_NAME,
    qdrant_url: str = QDRANT_URL,
    collection_name: str = COLLECTION_NAME):
    """
    Loads, processes, embeds JSON data, and indexes it into Qdrant.
    """
    logging.info(f"--- Starting Data Indexing into Qdrant (Collection: {collection_name}) ---")

    # 1. Load, process, and embed data using the new JSON function
    embedded_chunks = load_process_embed_json(json_dir=json_dir, model_name=model_name)
    if not embedded_chunks:
        logging.error("No embedded chunks generated from JSON. Aborting indexing.")
        return False

    vector_size = get_vector_size(model_name)
    logging.info(f"Using vector size: {vector_size} for model {model_name}")

    # 2. Connect to Qdrant
    logging.info(f"Connecting to Qdrant at {qdrant_url}")
    try:
        client = QdrantClient(url=qdrant_url)
        # Check connection implicitly by trying an operation (like listing collections)
        # client.health_check() # Removed deprecated health check
        # Perform a lightweight operation to check connectivity if needed before collection check
        client.get_collections() # This will raise an error if connection fails
        logging.info("Successfully connected to Qdrant.")
    except Exception as e:
        logging.error(f"Failed to connect or communicate with Qdrant at {qdrant_url}: {e}")
        logging.error("Please ensure Qdrant is running and accessible.")
        return False

    # 3. Ensure collection exists
    try:
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if collection_name not in collection_names:
            logging.info(f"Collection '{collection_name}' not found. Creating...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE) # Cosine distance is common for sentence embeddings
            )
            logging.info(f"Collection '{collection_name}' created successfully.")
        else:
            logging.info(f"Collection '{collection_name}' already exists.")
            # Optional: Check if vector params match, recreate if necessary (be careful!)
            # current_config = client.get_collection(collection_name).vectors_config
            # if current_config.params.size != vector_size or current_config.params.distance != Distance.COSINE:
            #     logging.warning(f"Collection parameters mismatch! Recreating collection '{collection_name}'. THIS WILL DELETE EXISTING DATA.")
            #     client.recreate_collection(...) # Use with caution

    except Exception as e:
        logging.error(f"Error managing Qdrant collection '{collection_name}': {e}")
        return False

    # 4. Prepare and upsert points
    points_to_upsert = []
    for chunk_data in embedded_chunks:
        # Generate a unique ID for each point
        point_id = str(uuid.uuid4())
        payload = {
            "text": chunk_data.get('text'),
            "source_file": chunk_data.get('source_file'),
            "source_url": chunk_data.get('source_url'),
            "image_urls": chunk_data.get('image_urls', []), # Ensure lists exist
            "link_urls": chunk_data.get('link_urls', [])
        }
        # Filter out None values from payload if necessary, though Qdrant might handle them
        payload = {k: v for k, v in payload.items() if v is not None}

        points_to_upsert.append(
            models.PointStruct(
                id=point_id,
                vector=chunk_data['embedding'],
                payload=payload
            )
        )

    if not points_to_upsert:
        logging.warning("No points prepared for upserting.")
        return True # Technically not an error, just nothing to do

    logging.info(f"Preparing to upsert {len(points_to_upsert)} points into '{collection_name}'...")
    try:
        # Upsert in batches for potentially large datasets
        client.upsert(
            collection_name=collection_name,
            points=points_to_upsert,
            wait=True # Wait for operation to complete
        )
        logging.info(f"Successfully upserted {len(points_to_upsert)} points.")
        return True
    except Exception as e:
        logging.error(f"Failed to upsert points into Qdrant collection '{collection_name}': {e}")
        return False

    logging.info("--- Data Indexing Finished ---")


if __name__ == "__main__":
    # Example: Run the indexing process directly using JSON data
    # You might want to add argument parsing here later if needed
    logging.info(f"Running indexer directly using JSON data from: {DEFAULT_JSON_DIR}")
    if index_data_to_qdrant(json_dir=DEFAULT_JSON_DIR, collection_name=COLLECTION_NAME):
        logging.info("Indexing completed successfully.")
    else:
        logging.error("Indexing failed.")
