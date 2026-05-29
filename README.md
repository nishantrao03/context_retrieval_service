# Context Retrieval Service

## Overview
The `context_retrieval_service` is a Python-based backend designed to handle the ingestion, storage, and retrieval of contextual information. This repository implements a system that not only stores normal information but also manages updates to the stored data. The service is built around two layers:

1. **Base Layer**: Stores the initial context or information.
2. **Update Layer**: Manages updates to the base layer, ensuring that the stored information remains current and relevant.

### Key Features
- **Ingestion**: Processes and stores raw data into the base or update layers.
- **Update Management**: Handles updates to existing data, ensuring consistency and accuracy.
- **Retrieval**: Retrieves relevant information based on stored data, leveraging a "5:5 functionality" that balances results from both the base and update layers.

### 5:5 Functionality
The retrieval process ensures that results are balanced between the base and update layers. Specifically, it retrieves 5 results from the base layer and 5 results from the update layer, providing a comprehensive view of the stored information.

---

## API Functionalities
This project exposes three main APIs:

### 1. **Ingestion Route (Building the Base Layer)**
- **Endpoint**: `/api/ingest`
- **Purpose**: Processes raw data and stores it in the base layer.
- **Workflow**:
  1. Accepts a file and metadata as input.
  2. Routes the file to the appropriate processing function based on its type (e.g., PDF, DOC).
  3. Calls `build_context_from_file` in `helpers/context_builder.py`:
     - Extracts and normalizes the data.
     - Chunks the data into smaller sections.
     - Embeds the chunks and stores them in the vector database.

### 2. **Update Ingestion Route (Building the Update Layer)**
- **Endpoint**: `/api/update`
- **Purpose**: Processes updates to existing data and stores them in the update layer.
- **Workflow**:
  1. Accepts update data and metadata as input.
  2. Routes the data to `update_context_retrieval` in `retrieval/update_context_retrieval.py`:
     - Processes the updates.
     - Ensures consistency with the base layer.

### 3. **Retrieval Route (Retrieving Information)**
- **Endpoint**: `/api/retrieve`
- **Purpose**: Retrieves relevant information from the stored data.
- **Workflow**:
  1. Accepts a query as input.
  2. Routes the query to `update_layer_retrieval` in `retrieval/update_layer_retrieval.py`:
     - Retrieves 5 results from the base layer.
     - Retrieves 5 results from the update layer.
     - Combines and returns the results.

---

## Setting Up the Project
Follow these steps to set up the project on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/nishantrao03/context_retrieval_service.git
cd context_retrieval_service
```

### 2. Set Up the Python Environment
- Ensure you have Python 3.8 or higher installed.
- Create a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate   # On Windows: venv\Scripts\activate
  ```

### 3. Install Dependencies
- Install the required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

### 4. Configure API Keys
- Create a `.env` file in the root directory with the following keys:
  ```env
  LLAMA_PARSER_API_KEY=<your_llama_parser_api_key>
  PINECONE_API_KEY=<your_pinecone_api_key>
  GEMINI_API_KEY=<your_gemini_api_key>
  ```
- Obtain the keys from the respective services:
  - **Llama Parser API Key**: [Llama Parser](https://cloud.llamaindex.ai/)
    - Log in, navigate to `API Keys`, and select `Generate New Key`.
    - Copy the key immediately as it will not be accessible later.
    - This key is used for parsing PDF documents.
  - **Pinecone API Key**: [Pinecone](https://app.pinecone.io)
    - Log in, select `Get Started`, and choose `Generate API Key`.
    - Provide a name for the key and optionally set permissions (available for upgraded accounts).
    - Copy the key immediately as it will not be accessible later.
    - This key is used for the vector database.
  - **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/)
    - Log in, navigate to `Get API Key`, and select `Create API Key`.
    - Provide a name and select a project (if applicable).
    - Copy the key immediately as it will not be accessible later.
    - This key is used for LLM-related tasks.

- **Important**: Always store the `.env` file securely and ensure it is added to `.gitignore` to prevent accidental exposure.

### 5. Run the Application
- Start the server:
  ```bash
  python app.py
  ```
- The server will be available at `http://localhost:8000`.

---

## ☁️ Google Drive API Integration

This project utilizes the Google Drive API to automatically upload files ingested from Slack and generate public viewing links. Because this app runs headless in production and uses a standard Google account (not a Workspace account), we use OAuth 2.0 User Credentials with a permanent Refresh Token strategy rather than a Service Account.

### Step 1: Google Cloud Setup & Authentication
To allow the backend to upload files to your personal Google Drive, you must generate an OAuth 2.0 Client ID.

**Enable the API:**
- Go to the Google Cloud Console, navigate to **APIs & Services > Library**, search for "Google Drive API", and click **Enable**.

**Configure the Consent Screen:**
- Go to **APIs & Services > OAuth consent screen**.
- Select **External** and click **Create**.
- Fill in the required App Name (e.g., Slack RAG Agent) and User Support Email.
- Skip the "Scopes" section (click Save and Continue).
- **CRITICAL:** Under the Test users section, click **+ Add Users** and type the exact personal Gmail address you will use to host the files.

**Generate Credentials:**
- Go to **APIs & Services > Credentials**.
- Click **+ CREATE CREDENTIALS > OAuth client ID**.
- Select **Desktop app** as the Application type.
- Click **Create** and click **DOWNLOAD JSON**.

### Step 2: Project Configuration
- Move the downloaded JSON file into the root directory of your Python project.
- Rename it to exactly `credentials.json`.

**Security Check:** Immediately open your `.gitignore` file and ensure the following lines are added. Never commit these files to version control.

```
# Google Drive API Secrets
credentials.json
token.json
```

### Step 3: Initializing the Token (First Run Only)
Before the server can run headlessly in the background, you must manually authorize it once to generate a permanent `token.json` file.

- Ensure you have a target folder created in your personal Google Drive and have copied its Folder ID (the long string of characters at the end of the folder's URL).
- Open `gdrive/gdrive_upload_helper.py` and temporarily paste your Folder ID into the test block at the bottom.
- Run the script locally:

```bash
python gdrive/gdrive_upload_helper.py
```

- A web browser will automatically open asking you to sign in.
- Log in using the exact Gmail address you added as a Test User.
- Click **Advanced** and proceed past the "Google hasn't verified this app" warning.
- Grant the requested permissions.
- Check your project root directory. A new file named `token.json` will have been generated. The backend will now use this file to authenticate silently in the background moving forward.

### Step 4: Pushing to Production (Bypassing the 7-Day Expiration)
By default, Google puts new apps in "Testing" mode, which strictly causes the `token.json` file to expire every 7 days. To make your headless authentication permanent, you must publish the app.

- Go back to the Google Cloud Console.
- Navigate to **APIs & Services > OAuth consent screen** (or Audience / Verification Center, depending on your console layout).
- Under Publishing status, click the **PUBLISH APP** (or "Push to Production") button.
- Accept the warning about Verification.

> **Note:** Because you are the only user logging into this app, you do not need to actually submit the app to Google for manual verification. Simply changing the status to "In production" permanently removes the 7-day expiration timer.

---

### 🚀 Usage in the Application
The logic is split into two secure modules:

- `gdrive_config.py`: Handles reading the `token.json` file, renewing the token silently if it expires, and establishing the Google Drive API connection.
- `gdrive_upload_helper.py`: Contains the `upload_file_to_gdrive(file_name, folder_id)` function.

When a file is passed from the Slack ingestion route, the helper function pushes it directly to the specified Drive folder in its native format (PDF, DOCX, etc.) and returns a viewable web link for the bot to serve back to the user.