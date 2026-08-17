# Context Retrieval Service

# 🎯 Overview

The Context Retrieval Service (CRS) is a dedicated backend responsible for managing project knowledge within Orchestra. It handles the complete lifecycle of project context, from document ingestion and update management to semantic retrieval and context deletion.

The service is built around a dual-layer knowledge architecture that separates stable project documents from evolving project updates. This allows project knowledge to evolve over time without modifying previously stored vectors, while maintaining consistent retrieval behavior.

---

# 💭 Motivation

Traditional RAG systems work well for static documents but become difficult to maintain when information changes over time.

Common challenges include:

- Updating information spread across multiple chunks
- Maintaining consistency across stored vectors
- Distinguishing stable documentation from evolving project updates
- Managing access to sensitive project knowledge

CRS addresses these challenges by structurally isolating stable documentation from evolving updates, ensuring continuous retrieval accuracy.

---

# ✨ Core Capabilities

<!-- Defines the primary operational scope and lifecycle management capabilities of the service. -->
* **📄 Document Ingestion:** Ingest project documents from supported sources, process them through a structured RAG pipeline, and store them in the knowledge base.
* **🔄 Update Ingestion:** Store project updates separately from documents using an update-specific pipeline designed around atomic fact extraction.
* **🔍 Semantic Retrieval:** Retrieve relevant project knowledge from both document and update layers using vector similarity search.
* **🗑️ Context Deletion:** Delete stored context using flexible metadata-based filters without requiring separate deletion workflows.
* **🔒 Privacy-Aware Knowledge Management:** Support public and private project knowledge with permission-aware retrieval.

---

# 🏗️ Key Architectural Features

<!-- Details the engineering methodologies and performance optimizations driving the system. -->
* **Dual-Layer Knowledge Architecture:** Project documents and project updates are stored separately, allowing knowledge to evolve without modifying previously stored vectors.
* **Section-Aware Chunking:** Documents are processed section-by-section before chunking, helping preserve document structure and semantic boundaries.
* **Privacy-Aware Retrieval:** Every stored chunk carries privacy metadata, enabling role-based retrieval of project knowledge.
* **Concurrent Ingestion Pipeline:** Document downloading and processing run concurrently using semaphore-controlled execution, improving ingestion throughput.
* **Optimized Embedding Pipeline:** Embedding models are initialized once during application startup and reused across requests.

This optimization reduced ingestion time for an 8-document workload from approximately **74 seconds to 24 seconds (~67% improvement).**

---

# 🏛️ High-Level Architecture

```text
                Orchestra
                     │
                     ▼
      Context Retrieval Service
                     │
                     ▼
                 Pinecone
```


### Orchestra

Responsible for:
- User interactions
- Project management
- Workflow execution
- Authorization
- Agent orchestration

### Context Retrieval Service

Responsible for:
- Document ingestion
- Update ingestion
- Semantic retrieval
- Context deletion
- Vector database interactions

---

# 🧠 Knowledge Architecture

CRS stores knowledge using two independent layers.

```text
          Documents
              │
              ▼
          Base Layer

          Updates
              │
              ▼
        Update Layer

              │
              ▼
          Retrieval
```

## Base Layer

Stores stable project knowledge such as:
- Requirements documents
- Specifications
- Design documents
- Meeting notes
- Project documentation

## Update Layer

Stores evolving project information such as:
- New decisions
- Project updates
- Requirement changes
- Status updates

## Why Two Layers?

Updating existing vectors can be difficult because relevant information may be distributed across multiple chunks.

Instead of modifying existing vectors, CRS stores updates in a dedicated update layer. During retrieval, both layers are searched independently and combined to provide a more complete view of project knowledge.

# 📄 Document Ingestion Pipeline

Document ingestion is responsible for building the Base Layer.

```text
Slack / Google Drive Link
            │
            ▼
       File Download
            │
            ▼
       Preprocessing
            │
            ▼
   Section Extraction
            │
            ▼
         Chunking
            │
            ▼
        Embedding
            │
            ▼
   Metadata Generation
            │
            ▼
         Pinecone
```

## Supported Sources

- Slack file uploads
- Google Drive file links

## Supported File Types

- PDF
- DOCX
- XLSX
- PPTX
- TXT

## Concurrent Processing

Files are downloaded and processed concurrently using a semaphore-based pipeline with a concurrency limit of four files.

## Preprocessing

PDF and non-PDF documents follow separate preprocessing paths. Both pipelines produce a normalized JSON representation containing structured document sections.

## Chunking

Documents are grouped by section before chunking.

Chunk generation uses:
- LangChain RecursiveCharacterTextSplitter
- HuggingFace tokenization
- Token-aware chunk boundaries

Current configuration:
- Chunk Size: 512 tokens
- Chunk Overlap: 75 tokens

## Embedding & Storage

Embeddings are generated using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Processed chunks are stored in Pinecone along with metadata describing the document, section, privacy level, and chunk information.

# 🔄 Update Ingestion Pipeline

Updates are processed differently from documents because updates are designed around facts rather than document structure.

```text
Project Update
      │
      ▼
  LLM Structuring
      │
      ▼
  Atomic Facts
      │
      ▼
 Context Creation
      │
      ▼
    Embedding
      │
      ▼
  Update Layer
```

## Atomic Fact Extraction

Updates are converted into structured JSON using an LLM.

Instead of storing large update blocks, updates are broken into smaller atomic facts that are easier to retrieve and reason about.

## Storage

The embedding is generated from the contextual representation of each update and stored in the update layer along with metadata such as:
- Atomic fact
- Context
- Privacy level
- Timestamp
- Source document reference

# 🔍 Retrieval Pipeline

Retrieval is designed to remain lightweight since it is expected to be the most frequently used operation.

```text
User Query
     │
     ▼
 Query Embedding
     │
     ▼
 Pinecone Search
     │
     ▼

5 Base Layer Results
5 Update Layer Results

     │
     ▼

 Combined Context
 ```

 ## Retrieval Strategy

The retrieval pipeline independently searches both knowledge layers.

Current retrieval behavior:
- Top 5 results from the Base Layer
- Top 5 results from the Update Layer

The combined results are returned to Orchestra for downstream processing.

# 🔒 Security Model

Security is implemented through chunk-level privacy metadata.

### Public Context

Accessible to:
- Project Members
- Project Managers

### Private Context

Accessible only to:
- Project Managers

### Permission-Aware Retrieval

Privacy metadata is preserved throughout ingestion, retrieval, and deletion operations, ensuring sensitive project information remains protected.

# 🗑️ Context Deletion

CRS supports metadata-driven deletion.

Instead of exposing multiple deletion APIs, a single deletion mechanism can remove context using combinations of metadata filters.

Examples include:
- Specific documents
- Entire projects
- Base layer chunks
- Update layer chunks
- Public context
- Private context

# 🌐 API Surface

| Endpoint | Purpose |
|----------|----------|
| `/api/ingest` | Document ingestion |
| `/api/update` | Update ingestion |
| `/api/retrieve` | Semantic retrieval |
| `/api/delete` | Context deletion |

# 🛠️ Tech Stack

| **Category** | **Technology** |
|--------------|----------------|
| Runtime | Python |
| Framework | FastAPI |
| Embeddings | Sentence Transformers |
| Vector Database | Pinecone |
| Document Parsing | LlamaParse |
| Chunking | LangChain |
| Tokenization | HuggingFace Transformers |

---

# 🚀 Getting Started

Clone the repository.

```bash
git clone https://github.com/nishantrao03/context_retrieval_service.git
cd context_retrieval_service
```

Create a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure the required environment variables.

```env
LLAMA_PARSER_API_KEY=
PINECONE_API_KEY=
SLACK_BOT_TOKEN=
```

Start the server.

```bash
python app.py
```

The service will be available at:

```text
http://localhost:8000
```

---

# 📄 License

This project is licensed under the MIT License.