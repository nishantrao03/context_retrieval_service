import uuid
from datetime import datetime, timezone

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def upsert_updates(
    atomic_facts,
    contexts,
    privacy_flags,
    context_embeddings,
    project_id,
    index_name=INDEX_NAME,
    document_id=None
):
    """
    Batch upserts update vectors into the update layer.
    """
    
    if not (
        len(atomic_facts)
        == len(contexts)
        == len(privacy_flags)
        == len(context_embeddings)
    ):
        raise ValueError(
            "Input lists must have the same length."
        )

    index = get_pinecone_index(
        index_name,
        EMBEDDING_DIMENSION
    )

    vectors = []

    timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    for i in range(len(atomic_facts)):

        vector_id = str(
            uuid.uuid4()
        )

        metadata = {
            "layer": "update_layer",
            "atomic_fact": atomic_facts[i],
            "context": contexts[i],
            "timestamp": timestamp,
            "is_private": privacy_flags[i]
        }

        if document_id:
            metadata["document_id"] = (
                document_id
            )

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