import uuid
from datetime import datetime, timezone

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def upsert_updates(
    atomic_facts,
    contexts,
    context_embeddings,
    project_id,
    index_name=INDEX_NAME,
    document_id=None
):
    """
    Batch upserts update vectors into the update layer.
    """

    index = get_pinecone_index(index_name, EMBEDDING_DIMENSION)

    timestamp = datetime.now(timezone.utc).isoformat()

    vectors = []

    for i in range(len(atomic_facts)):

        vector_id = str(uuid.uuid4())

        metadata = {
            "layer": "update_layer",
            "update_status": "active",
            "atomic_fact": atomic_facts[i],
            "context": contexts[i],
            "timestamp": timestamp
        }

        if document_id:
            metadata["document_id"] = document_id

        vectors.append({
            "id": vector_id,
            "values": context_embeddings[i],
            "metadata": metadata
        })

    if vectors:
        index.upsert(
            vectors=vectors,
            namespace=project_id
        )