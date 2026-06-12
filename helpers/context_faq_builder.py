from embeddings.embedder import TextEmbedder
from embeddings.upsert_faq import upsert_faq


async def build_faq_context(
    project_id: str,
    faq_json: list
):
    """
    Process FAQ entries and store them in Pinecone.
    """

    try:
        embedder = TextEmbedder()

        questions = [
            faq["question"]
            for faq in faq_json
        ]

        answers = [
            faq["answer"]
            for faq in faq_json
        ]

        question_embeddings = (
            embedder.embed_text_batch(
                questions
            )
        )

    except Exception as e:
        return {
            "status": "error",
            "stage": "embedding_generation",
            "error": str(e)
        }

    try:
        await upsert_faq(
            questions,
            answers,
            question_embeddings,
            project_id
        )

    except Exception as e:
        return {
            "status": "error",
            "stage": "faq_upsert",
            "error": str(e)
        }

    return {
        "status":
            "faq_ingestion_completed",

        "project_id":
            project_id,

        "faq_count":
            len(faq_json)
    }