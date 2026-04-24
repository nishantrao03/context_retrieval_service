from typing import Dict, Any, List

from embeddings.embedder import TextEmbedder
from retrieval.base_layer_retrieval import fetch_base_chunks
from retrieval.update_layer_retrieval import fetch_update_chunks


async def retrieve_chunks(query: str, project_id: str) -> Dict[str, List[Any]]:
    """
    Retrieves relevant chunks from base and update layers.
    """

    try:
        # Initialize embedder
        embedder = TextEmbedder()

        # Embed single query
        query_embedding = embedder.embed_text(query)

        # Fetch base layer chunks
        base_chunks = await fetch_base_chunks(
            query_embedding,
            project_id
        )

        # Fetch update layer chunks
        update_chunks = await fetch_update_chunks(
            query_embedding,
            project_id
        )

        return {
            "base_chunks": base_chunks,
            "update_chunks": update_chunks
        }

    except Exception as e:
        raise RuntimeError(f"retrieval_helper_failed: {str(e)}")