# routes/delete_route.py

from fastapi import APIRouter, Body, HTTPException

# Adjust the import path to access helpers from the root directory
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.delete_chunks import delete_chunks

# Initialize router
router = APIRouter()


@router.post("/api/delete")
async def delete_document_chunks(
    delete_operation: dict = Body(...)
):
    """ Delete document chunks from Pinecone using metadata filters. Example request body: { "project_id": "project_123", "metadata_filter": { "layer": "base_layer", "document_id": "doc_001" } } Example update layer deletion: { "project_id": "project_123", "metadata_filter": { "layer": "update_layer", "document_id": "doc_001" } } """

    if not isinstance(delete_operation, dict):
        raise HTTPException(
            status_code=400,
            detail="Input must be a JSON object."
        )

    try:
        deletion_result = await delete_chunks(
            delete_operation=delete_operation
        )

        return deletion_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chunk deletion failed: {str(e)}"
        )
