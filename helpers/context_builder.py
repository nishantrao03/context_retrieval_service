# helpers/context_builder.py

import os
import sys
from typing import Dict, Any

# Ensure the project root is in the system path to allow absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from ingestion.loaders.pdf_processor import parse_pdf
from ingestion.loaders.doc_extractor import extract_document
from ingestion.loaders.section_chunker import chunk_document
from embeddings.vector_indexer import index_vectors


def build_context_from_file(
    file_path: str,
    project_id: str,
    document_id: str,
    document_name: str,
    document_type: str
) -> Dict[str, Any]:
    """
    Main orchestrator function for the RAG pipeline.
    
    Phases:
    1. Extraction & Normalization: Routes PDF to pdf_processor, and other formats 
       to doc_extractor (which internally applies rule_based_normalization).
    2. Chunking: Passes normalized data to section_chunker.
    3. Embedding & Storage: Passes chunked data to vector_indexer.
    
    If any phase fails, the exception is raised immediately, halting the process.
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The target file at '{file_path}' does not exist.")
    
    # Standardize the document type for routing
    doc_type_clean = document_type.lower().strip()
    if doc_type_clean.startswith('.'):
        doc_type_clean = doc_type_clean[1:]

    # Phase 1: Pre-processing (Extraction and Normalization)
    try:
        if doc_type_clean == "pdf":
            # Executes ingestion/loaders/pdf_processor.py (Module 5)
            print(f"[ContextBuilder] Routing PDF to parse_pdf: {file_path}")
            normalized_data = parse_pdf(file_path)
        else:
            # Executes ingestion/loaders/doc_extractor.py (Module 3)
            # Note: doc_extractor natively calls rule_based_normalization (Module 4) internally
            print(f"[ContextBuilder] Routing General Doc to extract_document: {file_path}")
            # print("I reached here 1")
            normalized_data = extract_document(file_path)
            # print(normalized_data)  # Debugging output to verify normalization results
            
        if not normalized_data:
            raise ValueError("Extraction yielded no data. Halting process.")
            
    except Exception as e:
        print(f"[ContextBuilder] Phase 1 (Extraction) failed: {str(e)}")
        raise RuntimeError(f"Extraction failed: {str(e)}") from e

    # Phase 2: Chunking
    try:
        # Executes ingestion/loaders/section_chunker.py (Module 7)
        print("[ContextBuilder] Initiating chunking process...")
        chunked_data = chunk_document(
            normalized_json=normalized_data,
            project_id=project_id,
            document_id=document_id,
            document_name=document_name,
            document_type=document_type
        )
        
        if not chunked_data:
            raise ValueError("Chunking resulted in an empty dataset. Halting process.")
            
    except Exception as e:
        print(f"[ContextBuilder] Phase 2 (Chunking) failed: {str(e)}")
        raise RuntimeError(f"Chunking failed: {str(e)}") from e

    # Phase 3: Embedding and Vector DB Storage
    try:
        # Executes embeddings/vector_indexer.py (Module 6)
        print("[ContextBuilder] Initiating vector indexing and storage...")
        index_vectors(json_chunks=chunked_data, project_id=project_id)
        
    except Exception as e:
        print(f"[ContextBuilder] Phase 3 (Indexing) failed: {str(e)}")
        raise RuntimeError(f"Vector indexing failed: {str(e)}") from e

    # Final successful response mapping
    return {
        "status": "success",
        "project_id": project_id,
        "document_name": document_name,
        "chunks_processed": len(chunked_data),
        "message": "Document successfully extracted, chunked, and stored in vector database."
    }