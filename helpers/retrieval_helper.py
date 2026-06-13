from typing import Dict, Any, List

from embeddings.embedder import TextEmbedder
from retrieval.base_layer_retrieval import fetch_base_chunks
from retrieval.update_layer_retrieval import fetch_update_chunks
from retrieval.faq_layer_retreival import fetch_faq_chunks


async def retrieve_chunks(query: str, project_id: str, apply_privacy_filter: bool) -> Dict[str, List[Any]]:
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
            project_id,
            apply_privacy_filter
        )

        # Fetch update layer chunks
        update_chunks = await fetch_update_chunks(
            query_embedding,
            project_id,
            apply_privacy_filter
        )

        # # Fetch FAQ layer chunks
        # faq_chunks = await fetch_faq_chunks(
        #     query_embedding,
        #     project_id
        # )

        return {
            "base_chunks": base_chunks,
            "update_chunks": update_chunks,
            # "faq_chunks": faq_chunks
        }

    except Exception as e:
        raise RuntimeError(f"retrieval_helper_failed: {str(e)}")