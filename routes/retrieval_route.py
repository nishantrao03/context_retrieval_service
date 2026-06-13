from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from helpers.retrieval_helper import retrieve_chunks


router = APIRouter()


class RetrievalRequest(BaseModel):
    query: str
    project_id: str
    apply_privacy_filter: bool


@router.post("/api/retrieve")
async def retrieve_context(request: RetrievalRequest):
    """
    Handles retrieval API request and returns relevant chunks.
    """
    print(f"Received retrieval request: {request}")

    try:
        query = request.query
        project_id = request.project_id
        apply_privacy_filter = request.apply_privacy_filter
        print(f"Received retrieval request for project_id: {project_id} with query: {query}")

        if not query or not project_id:
            raise HTTPException(
                status_code=400,
                detail="query and project_id are required"
            )

        chunks = await retrieve_chunks(query, project_id, apply_privacy_filter)
        print(f"Retrieved chunks for project_id {project_id}: {chunks}")

        return {
            "status": "success",
            "project_id": project_id,
            "query": query,
            "apply_privacy_filter": apply_privacy_filter,
            "chunks": chunks
        }

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"retrieval_failed: {str(e)}"
        )