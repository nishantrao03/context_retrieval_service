import asyncio
from typing import List, Optional, Dict, Any

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384
TOP_K = 5
SIMILARITY_THRESHOLD = 0.9


async def _query_single_embedding(
    index,
    embedding: List[float],
    project_id: str,
    document_id: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Query Pinecone for a single embedding and filter by similarity threshold.
    """

    filter_query = {
        "layer": "update_layer",
        "update_status": "active"
    }

    if document_id:
        filter_query["document_id"] = document_id

    response = index.query(
        vector=embedding,
        top_k=TOP_K,
        include_metadata=True,
        namespace=project_id,
        filter=filter_query
    )

    print("Here goes Pinecone response: ", response)

    results = []

    matches = response.get("matches", [])
    print("Here goes matches: ", matches)
    for match in matches:
        print(match["score"])
        if match["score"] >= SIMILARITY_THRESHOLD:
            results.append({
                "chunk_id": match["id"],
                "score": match["score"],
                "metadata": match.get("metadata", {})
            })

    return results


async def fetch_update_chunks(
    search_query_embeddings: List[List[float]],
    update_types: List[str],
    project_id: str,
    index_name: str = INDEX_NAME,
    document_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch update chunks for all search query embeddings in parallel.
    """

    index = get_pinecone_index(index_name, EMBEDDING_DIMENSION)

    tasks = [
        _query_single_embedding(index, emb, project_id, document_id)
        if update_types[i] == "modification" else asyncio.sleep(0, result=[])
        for i, emb in enumerate(search_query_embeddings)
    ]

    results = await asyncio.gather(*tasks)

    ordered_results = []
    for res in results:
        ordered_results.append(res if res else [])

    return {
        "retrieved_update_chunks": ordered_results
    }