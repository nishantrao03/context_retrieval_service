# # routes/update_route.py

# import os
# import shutil
# import sys
# from typing import Optional
# from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# # Adjust the import path to access the project root
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.abspath(os.path.join(current_dir, '..'))
# if project_root not in sys.path:
#     sys.path.append(project_root)

# # Import the helper function (assuming it will be created in the helpers directory)
# from helpers.context_update_builder import build_update_context

# # Initialize the router
# router = APIRouter()

# # Define and create the llm_helper directory for file storage
# TEMP_DIR = os.path.join(project_root, 'llm_helper')
# os.makedirs(TEMP_DIR, exist_ok=True)

# # Set of allowed file extensions
# ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}

# @router.post("/api/update")
# async def update_document(
#     project_id: str = Form(...),
#     update_text: Optional[str] = Form(None),
#     file: Optional[UploadFile] = File(None)
# ):
#     """
#     API endpoint to receive an update via multipart/form-data.
#     Accepts either raw text or a file document. If a file is provided, 
#     it saves it temporarily to the llm_helper directory.
#     """
    
#     # 1. Validation Phase
#     if not update_text and not file:
#         raise HTTPException(
#             status_code=400, 
#             detail="You must provide either 'update_text' or a 'file'."
#         )
        
#     temp_file_path = None
#     file_extension = None
    
#     # 2. Temporary Storage Phase (Executed only if a file is uploaded)
#     if file and file.filename:
#         _, file_extension = os.path.splitext(file.filename)
#         file_extension = file_extension.lower()
        
#         if file_extension not in ALLOWED_EXTENSIONS:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Unsupported file type: {file_extension}. Allowed: {ALLOWED_EXTENSIONS}"
#             )
            
#         temp_file_path = os.path.join(TEMP_DIR, file.filename)
        
#         try:
#             with open(temp_file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to save file to disk: {str(e)}")

#     # 3. Processing Phase
#     try:
#         processing_result = build_update_context(
#             project_id=project_id,
#             update_text=update_text,
#             file_path=temp_file_path,
#             file_extension=file_extension
#         )
#         return processing_result
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Update Processing Error: {str(e)}")
        
#     finally:
#         # 4. Cleanup Phase
#         if temp_file_path and os.path.exists(temp_file_path):
#             os.remove(temp_file_path)
            
#         if file:
#             await file.close()

# routes/update_route.py

import os
import shutil
import sys
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.context_update_builder import build_update_context

router = APIRouter()

TEMP_DIR = os.path.join(project_root, 'llm_helper')
os.makedirs(TEMP_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}


@router.post("/api/update")
async def update_document(
    project_id: str = Form(...),
    update_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Receives update input and processes it through context builder.
    """

    # Validate input
    if not update_text and not file:
        raise HTTPException(
            status_code=400,
            detail="You must provide either 'update_text' or a 'file'."
        )

    temp_file_path = None
    file_extension = None

    # Save uploaded file temporarily
    if file and file.filename:
        _, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type: {file_extension}. "
                    f"Allowed: {ALLOWED_EXTENSIONS}"
                )
            )

        temp_file_path = os.path.join(TEMP_DIR, file.filename)

        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file to disk: {str(e)}"
            )

    try:
        # Await async context builder
        processing_result = await build_update_context(
            project_id=project_id,
            update_text=update_text,
            file_path=temp_file_path,
            file_extension=file_extension
        )

        return processing_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Update Processing Error: {str(e)}"
        )

    finally:
        # Cleanup temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        if file:
            await file.close()