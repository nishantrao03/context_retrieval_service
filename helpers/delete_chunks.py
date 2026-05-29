# helpers/delete_chunks.py

from typing import Dict, Any

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def delete_chunks(
    delete_operation: Dict[str, Any]
):
    """
    Delete chunks from Pinecone using metadata filters.
    """

    try:
        index = get_pinecone_index(
            INDEX_NAME,
            EMBEDDING_DIMENSION
        )

        project_id = delete_operation.get("project_id")
        metadata_filter = delete_operation.get("metadata_filter")

        if not project_id:
            return {
                "deletion_success": 0,
                "error_message": "Missing project_id"
            }

        if not metadata_filter:
            return {
                "project_id": project_id,
                "deletion_success": 0,
                "error_message": "Missing metadata_filter"
            }

        index.delete(
            namespace=project_id,
            filter=metadata_filter
        )

        return {
            "project_id": project_id,
            "deletion_success": 1
        }

    except Exception as e:
        return {
            "project_id": delete_operation.get("project_id"),
            "deletion_success": 0,
            "error_message": str(e)
        }
