from typing import List, Dict, Any

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def fetch_update_chunks(
    query_embedding: List[float],
    project_id: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Fetches top-k update layer chunks using vector similarity search.
    """

    try:
        index = get_pinecone_index(INDEX_NAME, EMBEDDING_DIMENSION)

        response = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=project_id,
            include_metadata=True,
            filter={
                "layer": "update_layer"
            }
        )

        matches = response.get("matches", [])

        results = []

        for match in matches:
            results.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata")
            })

        return results

    except Exception as e:
        raise RuntimeError(f"update_layer_retrieval_failed: {str(e)}")