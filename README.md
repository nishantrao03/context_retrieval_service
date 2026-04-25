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
  - **Gemini API Key**: [Google AI Studio](https://ai.google.com/)
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

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
