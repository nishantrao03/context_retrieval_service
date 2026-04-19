# pinecone_client.py

import os
from dotenv import load_dotenv
from pinecone import Pinecone


def get_pinecone_index(index_name: str, dimension: int):
    """
    Initializes the Pinecone client and connects to the specified index.
    If the index does not exist, it creates a new serverless index
    configured for manual vector storage.

    Args:
        index_name (str): The name of the vector index.
        dimension (int): The embedding vector dimension.

    Returns:
        Index: The Pinecone index object ready for operations.
    """

    # Resolve the path to the .env file located at the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_path)

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable is not set.")

    # Initialize the Pinecone client
    pc = Pinecone(api_key=api_key)

    # Create a standard vector index (NOT managed embedding)
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=dimension,      # Must match embedding model output
            metric="cosine",          # Since embeddings are normalized
            spec={
                "serverless": {
                    "cloud": "aws",
                    "region": "us-east-1"
                }
            }
        )

    # Return the connected index
    return pc.Index(index_name)