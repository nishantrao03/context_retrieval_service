# helpers/gdrive_file_download.py

import re
import asyncio
import aiohttp
import os


async def download_gdrive_file(
    session,
    google_drive_url: str,
    temp_file_path: str
):
    """
    Download a Google Drive file and save it temporarily.
    """
    if not google_drive_url:
        raise Exception(
            "google_drive_url is required."
        )

    if not temp_file_path:
        raise Exception(
            "temp_file_path is required."
        )

    file_id = None

    patterns = [
        r"/file/d/([^/]+)",
        r"/document/d/([^/]+)",
        r"/spreadsheets/d/([^/]+)",
        r"/presentation/d/([^/]+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            google_drive_url
        )

        if match:
            file_id = match.group(1)
            break

    if not file_id:
        raise Exception(
            "Invalid Google Drive file URL."
        )

    download_url = (
        f"https://drive.google.com/uc?export=download&id={file_id}"
    )

    async with session.get(download_url) as response:

        if response.status != 200:
            raise Exception(
                f"Google Drive file download failed with status code {response.status}"
            )

        content_disposition = (
            response.headers.get(
                "Content-Disposition"
            )
        )

        if not content_disposition:
            raise Exception(
                "Content-Disposition header not found."
            )

        filename_match = re.search(
            r'filename="([^"]+)"',
            content_disposition
        )

        if not filename_match:
            raise Exception(
                "Unable to extract filename."
            )

        document_name = (
            filename_match.group(1)
        )

        document_type = (
            os.path.splitext(
                document_name
            )[1]
            .replace(".", "")
            .lower()
        )

        with open(temp_file_path, "wb") as file:
            file.write(
                await response.read()
            )

    return {
        "temp_file_path":
            temp_file_path,

        "document_name":
            document_name,

        "document_type":
            document_type,
    }


if __name__ == "__main__":
    async def main():
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        temp_file_path = os.path.join(
            project_root,
            "ingestion",
            "temp_uploads",
            "AI_Applications_Ethics_Future.docx"
        )

        async with aiohttp.ClientSession() as session:
            result = await download_gdrive_file(
                session=session,
                google_drive_url=
                    "https://docs.google.com/document/d/19W7bolsPr7WWrCyJwRGcf8br8yCG0oLS/edit?usp=sharing&ouid=116006106231977998356&rtpof=true&sd=true",
                temp_file_path=
                    temp_file_path
            )

            print(result)

    asyncio.run(main())