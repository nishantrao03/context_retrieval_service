# helpers/gdrive_file_download.py

import re


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
            print(response)
            raise Exception(
                # print(response)
                f"Google Drive file download failed with status code {response.status}"
            )

        with open(temp_file_path, "wb") as file:
            file.write(await response.read())

    return temp_file_path