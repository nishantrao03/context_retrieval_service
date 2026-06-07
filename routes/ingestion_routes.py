# # routes/ingestion_routes.py

# import os
# import shutil
# import json
# from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# # Adjust the import path to access context_builder from the root directory
# import sys
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.abspath(os.path.join(current_dir, '..'))
# if project_root not in sys.path:
#     sys.path.append(project_root)

# from helpers.context_builder import build_context_from_file

# # Initialize the router to be included in app.py later
# router = APIRouter()

# # Define and create the temporary storage directory
# TEMP_DIR = os.path.join(project_root, 'ingestion', 'temp_uploads')
# os.makedirs(TEMP_DIR, exist_ok=True)

# # Set of allowed file extensions based on current pipeline capabilities
# ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}

# @router.post("/api/ingest")
# async def ingest_document(
#     files: list[UploadFile] = File(...),
#     metadata: str = Form(...)
# ):
#     """
#     API endpoint to receive an array of objects (file and metadata), validate them,
#     save them temporarily, and process each through the RAG pipeline.
#     """
#     try:
#         metadata_list = json.loads(metadata)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid metadata format. Expected JSON string.")

#     if len(files) != len(metadata_list):
#         raise HTTPException(status_code=400, detail="Mismatch between files and metadata length.")

#     final_results = []

#     for i, file in enumerate(files):
#         meta = metadata_list[i]
#         project_id = meta.get("project_id")
#         document_id = meta.get("document_id")
#         document_type = meta.get("document_type")

#         # 1. Validation Phase
#         if not file.filename:
#             raise HTTPException(status_code=400, detail="No file name provided.")
            
#         _, file_extension = os.path.splitext(file.filename)
#         file_extension = file_extension.lower()
        
#         if file_extension not in ALLOWED_EXTENSIONS:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Unsupported file type: {file_extension}. Allowed: {ALLOWED_EXTENSIONS}"
#             )

#         # 2. Temporary Storage Phase
#         # Construct a safe path to store the incoming binary stream
#         temp_file_path = os.path.join(TEMP_DIR, file.filename)
        
#         try:
#             # Write the binary bytes from the request directly to the hard drive
#             with open(temp_file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
                
#             # 3. Processing Phase
#             processing_result = build_context_from_file(
#                 file_path=temp_file_path,
#                 project_id=project_id,
#                 document_id=document_id,
#                 document_name=file.filename,
#                 document_type=document_type
#             )
#             final_results.append(processing_result)
            
#         except Exception as e:
#             # Catch errors from the RAG pipeline (parsing, chunking, or Pinecone)
#             raise HTTPException(status_code=500, detail=f"RAG Processing Error: {str(e)}")
            
#         finally:
#             # 4. Cleanup Phase
#             # This block executes regardless of success or failure to prevent disk space leaks
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)
                
#             # Ensure the file object is closed
#             await file.close()

#     return final_results

# routes/ingestion_routes.py

import os
import asyncio
import aiohttp
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body

# Adjust the import path to access helpers from the root directory
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.context_builder import build_context_from_file
from helpers.slack_file_download import download_slack_file
from helpers.gdrive_file_download import download_gdrive_file

# Initialize the router to be included in app.py later
router = APIRouter()

# Define and create the temporary storage directory
TEMP_DIR = os.path.join(project_root, 'ingestion', 'temp_uploads')
os.makedirs(TEMP_DIR, exist_ok=True)

# Set of allowed file extensions based on current pipeline capabilities
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}

# Maximum concurrent ingestion processes
INGESTION_SEMAPHORE = asyncio.Semaphore(4)


def get_timestamp():
    """
    Return formatted timestamp for temporary debugging logs.
    """
    return datetime.now().strftime("%H:%M:%S")


async def process_file(
    session,
    file_metadata: dict
):
    """
    Process a single file through download and ingestion pipeline.
    """
    async with INGESTION_SEMAPHORE:
        download_url = file_metadata["download_url"]
        source = file_metadata["source"]
        project_id = file_metadata["project_id"]
        document_id = file_metadata["document_id"]
        document_type = file_metadata["document_type"]
        document_name = file_metadata["document_name"]

        file_name_without_extension, file_extension = os.path.splitext(
            document_name
        )

        temp_document_name = (
            f"{file_name_without_extension}_{document_id}{file_extension}"
        )

        temp_file_path = os.path.join(
            TEMP_DIR,
            temp_document_name
        )

        try:
            print(
                f"[{get_timestamp()}] "
                f"PROCESS_STARTED | document_id={document_id}"
            )

            # Download Phase
            if source == "slack":
                await download_slack_file(
                    session=session,
                    private_download_url=download_url,
                    temp_file_path=temp_file_path
                )

            elif source == "google_drive":
                await download_gdrive_file(
                    session=session,
                    google_drive_url=download_url,
                    temp_file_path=temp_file_path
                )

            else:
                raise Exception(
                    f"Unsupported source: {source}"
                )

            print(
                f"[{get_timestamp()}] "
                f"DOWNLOAD_COMPLETED | document_id={document_id}"
            )

            # Processing Phase
            processing_result = await asyncio.to_thread(
                build_context_from_file,
                file_path=temp_file_path,
                project_id=project_id,
                document_id=document_id,
                document_name=document_name,
                document_type=document_type
            )

            print(
                f"[{get_timestamp()}] "
                f"INGESTION_COMPLETED | document_id={document_id}"
            )

            return {
                "document_id": document_id,
                "ingestion_success": 1
            }

        except Exception as e:
            print(
                f"[{get_timestamp()}] "
                f"INGESTION_FAILED | document_id={document_id} | error={str(e)}"
            )

            return {
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": str(e)
            }

        finally:
            # Cleanup Phase
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


@router.post("/api/ingest")
async def ingest_document(
    files_metadata: list[dict] = Body(...)
):
    """
    Expected payload:

    [
        {
            "download_url": "",
            "source": "",
            "project_id": "",
            "document_id": "",
            "document_type": "",
            "document_name": ""
        }
    ]

    API endpoint to receive file metadata,
    download files, and process them through the RAG pipeline.
    """
    if not isinstance(files_metadata, list):
        raise HTTPException(
            status_code=400,
            detail="Input must be an array of file metadata objects."
        )

    if not files_metadata:
        raise HTTPException(
            status_code=400,
            detail="No file metadata received."
        )

    validated_files_metadata = []
    validation_results = []

    # Validation Phase
    for file_metadata in files_metadata:
        download_url = file_metadata.get("download_url")
        source = file_metadata.get("source")
        project_id = file_metadata.get("project_id")
        document_id = file_metadata.get("document_id")
        document_type = file_metadata.get("document_type")
        document_name = file_metadata.get("document_name")

        if not download_url:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": "Missing download_url"
            })
            continue

        if not source:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": "Missing source"
            })
            continue

        if not project_id:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": "Missing project_id"
            })
            continue

        if not document_id:
            validation_results.append({
                "document_id": None,
                "ingestion_success": 0,
                "error_message": "Missing document_id"
            })
            continue

        if not document_type:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": "Missing document_type"
            })
            continue

        if not document_name:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": "Missing document_name"
            })
            continue

        _, file_extension = os.path.splitext(document_name)
        file_extension = file_extension.lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            validation_results.append({
                "document_id": document_id,
                "ingestion_success": 0,
                "error_message": (
                    f"Unsupported file type: {file_extension}. "
                    f"Allowed: {ALLOWED_EXTENSIONS}"
                )
            })
            continue

        validated_files_metadata.append(file_metadata)

    try:
        async with aiohttp.ClientSession() as session:

            ingestion_tasks = [
                process_file(session, file_metadata)
                for file_metadata in validated_files_metadata
            ]

            processing_results = await asyncio.gather(*ingestion_tasks)

        return validation_results + processing_results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline failed: {str(e)}"
        )