import json
import uuid
from collections import defaultdict
from typing import List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer


# -----------------------------
# Configuration
# -----------------------------

MAX_TOKENS = 512
CHUNK_OVERLAP = 75
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# -----------------------------
# Helper: Token Counter
# -----------------------------

class TokenLengthFunction:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def __call__(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))


# -----------------------------
# Core Chunking Function
# -----------------------------

def chunk_document(
    normalized_json: List[Dict],
    project_id: str,
    document_id: str,
    document_name: str,
    document_type: str
) -> List[Dict]:

    # Group entries by section
    sections = defaultdict(list)
    for entry in normalized_json:
        section_name = entry["section"]
        sections[section_name].append(entry)

    # Token length function
    length_function = TokenLengthFunction(EMBEDDING_MODEL_NAME)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_TOKENS,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=length_function,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    final_chunks = []

    for section_name, entries in sections.items():

        # Merge text within section
        merged_text_parts = []
        section_type = entries[0]["type"]

        for e in entries:
            merged_text_parts.append(e["text"])

        merged_text = "\n".join(merged_text_parts)

        # Split using token-aware splitter
        section_chunks = splitter.split_text(merged_text)

        total_chunks_in_section = len(section_chunks)

        for idx, chunk_text in enumerate(section_chunks):
            chunk_id = f"{project_id}_{document_id}_{section_name.replace(' ', '_')}_{idx}"

            chunk_object = {
                "chunk_id": chunk_id,

                "document_id": document_id,
                "document_name": document_name,
                "document_type": document_type,

                "section": section_name,
                "type": section_type,

                "chunk_index": idx,
                "section_chunk_count": total_chunks_in_section,

                "text": chunk_text,
                "token_count": length_function(chunk_text)
            }

            final_chunks.append(chunk_object)

    return final_chunks


# -----------------------------
# Test Main Function
# -----------------------------

def main():
    input_file = "final_output.txt"
    output_file = "output_part_2.txt"

    project_id = "project_2"
    document_id = "doc_1"
    document_name = "doctest.docx"
    document_type = "docx"

    with open(input_file, "r", encoding="utf-8") as f:
        normalized_json = json.load(f)

    chunked_output = chunk_document(
        normalized_json=normalized_json,
        project_id=project_id,
        document_id=document_id,
        document_name=document_name,
        document_type=document_type
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunked_output, f, indent=4, ensure_ascii=False)

    print(f"Chunking complete. Output written to {output_file}")


if __name__ == "__main__":
    main()

# ingestion/loaders/section_chunker.py

# import json
# from collections import defaultdict
# from typing import List, Dict

# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from transformers import AutoTokenizer


# # -----------------------------
# # Configuration
# # -----------------------------

# MAX_TOKENS = 512
# CHUNK_OVERLAP = 75
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# # -----------------------------
# # Helper: Token Counter
# # -----------------------------

# class TokenLengthFunction:
#     def __init__(self, model_name: str):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)

#     def __call__(self, text: str) -> int:
#         return len(self.tokenizer.encode(text, add_special_tokens=False))


# # -----------------------------
# # Core Chunking Function
# # -----------------------------

# def chunk_document(
#     normalized_json: List[Dict],
#     project_id: str,
#     document_id: str,
#     document_name: str,
#     document_type: str
# ) -> List[Dict]:

#     # Group entries by section
#     sections = defaultdict(list)
#     for entry in normalized_json:
#         # Use .get() to safely handle missing keys, defaults to None if not present
#         section_name = entry.get("section")
#         sections[section_name].append(entry)

#     # Token length function
#     length_function = TokenLengthFunction(EMBEDDING_MODEL_NAME)

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=MAX_TOKENS,
#         chunk_overlap=CHUNK_OVERLAP,
#         length_function=length_function,
#         separators=["\n\n", "\n", ".", " ", ""],
#     )

#     final_chunks = []

#     for section_name, entries in sections.items():

#         # Merge text within section
#         merged_text_parts = []
#         section_type = entries[0].get("type", "unknown")

#         for e in entries:
#             merged_text_parts.append(e["text"])

#         merged_text = "\n".join(merged_text_parts)

#         # Split using token-aware splitter
#         section_chunks = splitter.split_text(merged_text)

#         total_chunks_in_section = len(section_chunks)

#         # Fallback for NoneType sections
#         safe_section_name = str(section_name).replace(' ', '_') if section_name else "General"
#         display_section_name = section_name if section_name else "General"

#         for idx, chunk_text in enumerate(section_chunks):
#             # Safely create chunk_id without crashing on None
#             chunk_id = f"{project_id}_{document_id}_{safe_section_name}_{idx}"

#             chunk_object = {
#                 "chunk_id": chunk_id,
#                 "project_id": project_id,
                
#                 "document_id": document_id,
#                 "document_name": document_name,
#                 "document_type": document_type,

#                 "section": display_section_name,
#                 "type": section_type,

#                 "chunk_index": idx,
#                 "section_chunk_count": total_chunks_in_section,

#                 "text": chunk_text,
#                 "token_count": length_function(chunk_text)
#             }

#             final_chunks.append(chunk_object)

#     return final_chunks