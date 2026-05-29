# helpers/slack_file_download.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack bot token used for authenticated file downloads
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


async def download_slack_file(
    session,
    private_download_url: str,
    temp_file_path: str
):
    """
    Download a Slack file and save it temporarily.
    """
    if not SLACK_BOT_TOKEN:
        raise Exception(
            "SLACK_BOT_TOKEN is missing in environment variables."
        )

    if not private_download_url:
        raise Exception(
            "private_download_url is required."
        )

    if not temp_file_path:
        raise Exception(
            "temp_file_path is required."
        )

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
    }

    async with session.get(
        private_download_url,
        headers=headers
    ) as response:

        if response.status != 200:
            raise Exception(
                f"Slack file download failed with status code {response.status}"
            )

        with open(temp_file_path, "wb") as file:
            file.write(await response.read())

    return temp_file_path