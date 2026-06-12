import uuid
from datetime import datetime, timezone

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def upsert_faq(
    questions,
    answers,
    question_embeddings,
    project_id,
    index_name=INDEX_NAME
):
    """
    Batch upserts FAQ vectors into the FAQ layer.
    """

    if not (
        len(questions)
        == len(answers)
        == len(question_embeddings)
    ):
        raise ValueError(
            "Input lists must have the same length."
        )

    index = get_pinecone_index(
        index_name,
        EMBEDDING_DIMENSION
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    vectors = []

    for i in range(
        len(questions)
    ):
        vector_id = str(
            uuid.uuid4()
        )

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        metadata = {
            "layer": "faq_layer",
            "question": questions[i],
            "answer": answers[i],
            "timestamp": timestamp
        }

        vectors.append({
            "id": vector_id,
            "values": question_embeddings[i],
            "metadata": metadata
        })

    if vectors:
        index.upsert(
            vectors=vectors,
            namespace=project_id
        )