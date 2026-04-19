# routes/ingestion_routes.py

import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# Adjust the import path to access context_builder from the root directory
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.context_builder import build_context_from_file

# Initialize the router to be included in app.py later
router = APIRouter()

# Define and create the temporary storage directory
TEMP_DIR = os.path.join(project_root, 'ingestion', 'temp_uploads')
os.makedirs(TEMP_DIR, exist_ok=True)

# Set of allowed file extensions based on current pipeline capabilities
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}

@router.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    document_id: str = Form(...),
    document_type: str = Form(...)
):
    """
    API endpoint to receive a document via multipart/form-data, validate it,
    save it temporarily, and process it through the RAG pipeline.
    """
    
    # 1. Validation Phase
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")
        
    _, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # 2. Temporary Storage Phase
    # Construct a safe path to store the incoming binary stream
    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        # Write the binary bytes from the request directly to the hard drive
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file to disk: {str(e)}")

    # 3. Processing Phase
    try:
        # Pass the newly created file path to the orchestrator
        processing_result = build_context_from_file(
            file_path=temp_file_path,
            project_id=project_id,
            document_id=document_id,
            document_name=file.filename,
            document_type=document_type
        )
        
        return processing_result
        
    except Exception as e:
        # Catch errors from the RAG pipeline (parsing, chunking, or Pinecone)
        raise HTTPException(status_code=500, detail=f"RAG Processing Error: {str(e)}")
        
    # finally:
    #     # 4. Cleanup Phase
    #     # This block executes regardless of success or failure to prevent disk space leaks
    #     if os.path.exists(temp_file_path):
    #         os.remove(temp_file_path)
            
    #     # Ensure the file object is closed
    #     await file.close()