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
        download_url = file_metadata.get("download_url")
        source = file_metadata["source"]
        project_id = file_metadata["project_id"]
        document_id = file_metadata["document_id"]
        document_type = file_metadata["document_type"]
        document_name = file_metadata["document_name"]
        text_content = file_metadata.get(
            "text_content"
        )
        is_private = file_metadata.get(
            "is_private", False
        )

        if source == "slack":
            file_name_without_extension, file_extension = os.path.splitext(
                document_name
            )

            temp_document_name = (
                f"{file_name_without_extension}_{document_id}{file_extension}"
            )

        elif source == "google_drive":
            temp_document_name = (
                f"gdrive_{document_id}"
            )

        elif source == "text":
            temp_document_name = (
                f"{document_name}.txt"
            )

        else:
            raise Exception(
                f"Unsupported source: {source}"
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
                download_result = await download_gdrive_file(
                    session=session,
                    google_drive_url=download_url,
                    temp_file_path=temp_file_path
                )

                document_name = (
                    download_result["document_name"]
                )

                document_type = (
                    download_result["document_type"]
                )

                _, file_extension = os.path.splitext(
                    document_name
                )

                file_extension = (
                    file_extension.lower()
                )

                if file_extension not in ALLOWED_EXTENSIONS:
                    raise Exception(
                        f"Unsupported file type: {file_extension}. "
                        f"Allowed: {ALLOWED_EXTENSIONS}"
                    )

            elif source == "text":
                with open(
                    temp_file_path,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(
                        text_content
                    )

                document_type = (
                    "txt"
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
                document_type=document_type,
                is_private=is_private
            )

            print(
                f"[{get_timestamp()}] "
                f"INGESTION_COMPLETED | document_id={document_id}"
            )

            return {
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 1
            }

        except Exception as e:
            print(
                f"[{get_timestamp()}] "
                f"INGESTION_FAILED | document_id={document_id} | error={str(e)}"
            )

            return {
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": str(e)
            }

        finally:
    # Cleanup Phase
            if (
                temp_file_path
                and os.path.exists(
                    temp_file_path
                )
            ):
            
                os.remove(
                    temp_file_path
                )   


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
            "document_name": "",
            "text_content": "",
            "is_private": False
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
        text_content = file_metadata.get(
            "text_content"
        )

        if "is_private" in file_metadata and not isinstance(file_metadata["is_private"], bool):
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "is_private must be a boolean value"
            })
            continue

        if not source:
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing source"
            })
            continue

        if (
            source != "text"
            and not download_url
        ):
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing download_url"
            })
            continue

        if not project_id:
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing project_id"
            })
            continue

        if not document_id:
            validation_results.append({
                "document_id": None,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing document_id"
            })
            continue

        if (
            source == "text"
            and not text_content
        ):
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing text_content"
            })
            continue

        if (
            source == "slack"
            and not document_type
        ):
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing document_type"
            })
            continue

        if (
            source == "slack"
            and not document_name
        ):
            validation_results.append({
                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,
                "ingestion_success": 0,
                "error_message": "Missing document_name"
            })
            continue

        if (
            source == "slack"
        ):
            _, file_extension = os.path.splitext(
                document_name
            )

            file_extension = (
                file_extension.lower()
            )

            if file_extension not in ALLOWED_EXTENSIONS:
                validation_results.append({
                    "document_id": document_id,
                    "document_name": document_name,
                    "document_type": document_type,
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