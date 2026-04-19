# # doc_extractor.py

# import os
# from typing import List, Dict, Any
# from unstructured.partition.auto import partition


# def extract_document(file_path: str) -> List[Dict[str, Any]]:
#     """
#     Extracts structured content from a document using the unstructured library.
    
#     Args:
#         file_path (str): The absolute or relative path to the document file.
        
#     Returns:
#         List[Dict[str, Any]]: A list of dictionaries representing extracted elements.
#                               Each dict contains 'type', 'text', and 'metadata'.
                              
#     Raises:
#         FileNotFoundError: If the file_path does not exist.
#         RuntimeError: If document extraction fails.
#     """
#     # 1. Validate file existence
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"The file at '{file_path}' was not found.")

#     try:
#         # 2. auto-partition the document (handles PDF, DOCX, PPTX, XLSX, TXT, etc.)
#         elements = partition(filename=file_path)
#     except Exception as e:
#         # Wrap library-specific exceptions in a clear RuntimeError
#         raise RuntimeError(f"Failed to extract content from '{file_path}': {str(e)}") from e

#     extracted_data: List[Dict[str, Any]] = []

#     # 3. Convert elements to the specified dictionary format
#     for element in elements:
#         # 'category' usually maps to the element type (e.g., Title, NarrativeText)
#         # We ensure metadata is converted to a dict if available
#         meta_dict = element.metadata.to_dict() if hasattr(element.metadata, "to_dict") else {}
        
#         entry = {
#             "type": getattr(element, "category", "UncategorizedText"),
#             "text": str(element),  # Raw text content
#             "metadata": meta_dict
#         }
#         extracted_data.append(entry)

#     return extracted_data


# # ---------------- TEMP TEST ----------------
# if __name__ == "__main__":
#     # This block allows you to run the file directly to test extraction
#     import sys
#     import json
    
#     # Use a dummy path or a file passed as an argument
#     test_path = sys.argv[1] if len(sys.argv) > 1 else "pdftext.pdf"  # Replace with an actual file path for testing
    
#     print(f"--- Extracting from: {test_path} ---")
#     try:
#         data = extract_document(test_path)
#         print(f"Successfully extracted {len(data)} elements.\n")

#         # Save the full structured output to temp.txt
#         output_path = os.path.join(os.path.dirname(__file__), "temp.txt")
#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, default=str)
#         print(f"Full output written to: {output_path}\n")
        
#         for i, item in enumerate(data):
#             print(f"Element {i}:")
#             print(f"  Type: {item['type']}")
#             print(f"  Text: {item['text'][:100]}...") # Truncate for display
#             print(f"  Meta: keys={list(item['metadata'].keys())}")
#             print()
            
#     except Exception as err:
#         print(f"Error: {err}")

# doc_extractor.py

# NOTE: This logic is for all file types except PDF.

# import os
# from typing import List, Dict, Any
# from unstructured.partition.auto import partition
# from ingestion.loaders.rule_based_normalization import normalize_unstructured_output
# # from rule_based_normalization import normalize_unstructured_output


# def extract_document(file_path: str) -> List[Dict[str, Any]]:
#     """
#     Extracts structured content from a document using the unstructured library
#     and then normalizes it using rule-based logic.
    
#     Args:
#         file_path (str): The absolute or relative path to the document file.
        
#     Returns:
#         List[Dict[str, Any]]: A list of dictionaries representing the final 
#                               normalized chunks ready for embedding.
                              
#     Raises:
#         FileNotFoundError: If the file_path does not exist.
#         RuntimeError: If document extraction fails.
#     """
#     # 1. Validate file existence
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"The file at '{file_path}' was not found.")

#     try:
#         # 2. auto-partition the document (handles DOCX, PPTX, XLSX, TXT, etc.)
#         elements = partition(filename=file_path)
#     except Exception as e:
#         # Wrap library-specific exceptions in a clear RuntimeError
#         raise RuntimeError(f"Failed to extract content from '{file_path}': {str(e)}") from e

#     extracted_data: List[Dict[str, Any]] = []

#     # 3. Convert elements to the specified dictionary format
#     for element in elements:
#         # 'category' usually maps to the element type (e.g., Title, NarrativeText)
#         # We ensure metadata is converted to a dict if available
#         meta_dict = element.metadata.to_dict() if hasattr(element.metadata, "to_dict") else {}
        
#         entry = {
#             "type": getattr(element, "category", "UncategorizedText"),
#             "text": str(element),  # Raw text content
#             "metadata": meta_dict
#         }
#         extracted_data.append(entry)

#     # print(extracted_data)  # Debugging output to verify extraction results

#     # 4. Pass the extracted raw JSON to the normalization rule engine
#     final_normalized_data = normalize_unstructured_output(extracted_data)

#     # print(final_normalized_data)  

#     return final_normalized_data


# # ---------------- TEMP TEST ----------------
# if __name__ == "__main__":
#     # This block allows you to run the file directly to test extraction
#     import sys
#     import json
    
#     # Use a dummy path or a file passed as an argument
#     test_path = sys.argv[1] if len(sys.argv) > 1 else "Global_Warming_Expanded_Sections.docx"  # Replace with an actual file path for testing
    
#     print(f"--- Extracting from: {test_path} ---")
#     try:
#         data = extract_document(test_path)
#         print(f"Successfully extracted {len(data)} elements.\n")

#         # Save the full structured output to temp.txt
#         output_path = os.path.join(os.path.dirname(__file__), "final_output.txt")
#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, default=str)
#         print(f"Full output written to: {output_path}\n")
        
#         for i, item in enumerate(data):
#             print(f"Element {i}:")
#             print(f"  Type: {item['type']}")
#             print(f"  Text: {item['text'][:100]}...") # Truncate for display
#             # print(f"  Meta: keys={list(item['metadata'].keys())}")
#             print()
            
#     except Exception as err:
#         print(f"Error: {err}")

# doc_extractor.py

# NOTE: This logic is for all file types except PDF.

import os
from typing import List, Dict, Any
from unstructured.partition.auto import partition
from ingestion.loaders.rule_based_normalization import normalize_unstructured_output


def extract_document(file_path: str, is_update: bool = False) -> List[Dict[str, Any]]:
    """
    Extracts structured content from a document using the unstructured library
    and then normalizes it using rule-based logic.
    
    Args:
        file_path (str): The absolute or relative path to the document file.
        is_update (bool): If True, bypasses rule-based normalization and returns raw chunks.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the extracted chunks.
                              
    Raises:
        FileNotFoundError: If the file_path does not exist.
        RuntimeError: If document extraction fails.
    """
    # 1. Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file at '{file_path}' was not found.")

    try:
        # 2. auto-partition the document (handles DOCX, PPTX, XLSX, TXT, etc.)
        elements = partition(filename=file_path)
    except Exception as e:
        # Wrap library-specific exceptions in a clear RuntimeError
        raise RuntimeError(f"Failed to extract content from '{file_path}': {str(e)}") from e

    extracted_data: List[Dict[str, Any]] = []

    # 3. Convert elements to the specified dictionary format
    for element in elements:
        # 'category' usually maps to the element type (e.g., Title, NarrativeText)
        # We ensure metadata is converted to a dict if available
        meta_dict = element.metadata.to_dict() if hasattr(element.metadata, "to_dict") else {}
        
        entry = {
            "type": getattr(element, "category", "UncategorizedText"),
            "text": str(element),  # Raw text content
            "metadata": meta_dict
        }
        extracted_data.append(entry)

    # If this is an update document, return the raw data without passing it through 
    # the rigid rule-based normalization engine.
    if is_update:
        return extracted_data

    # 4. Pass the extracted raw JSON to the normalization rule engine for standard ingestion
    final_normalized_data = normalize_unstructured_output(extracted_data)

    return final_normalized_data


# ---------------- TEMP TEST ----------------
if __name__ == "__main__":
    # This block allows you to run the file directly to test extraction
    import sys
    import json
    
    # Use a dummy path or a file passed as an argument
    test_path = sys.argv[1] if len(sys.argv) > 1 else "Global_Warming_Expanded_Sections.docx"  # Replace with an actual file path for testing
    
    print(f"--- Extracting from: {test_path} ---")
    try:
        data = extract_document(test_path)
        print(f"Successfully extracted {len(data)} elements.\n")

        # Save the full structured output to temp.txt
        output_path = os.path.join(os.path.dirname(__file__), "final_output.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)
        print(f"Full output written to: {output_path}\n")
        
        for i, item in enumerate(data):
            print(f"Element {i}:")
            print(f"  Type: {item['type']}")
            print(f"  Text: {item['text'][:100]}...") # Truncate for display
            # print(f"  Meta: keys={list(item['metadata'].keys())}")
            print()
            
    except Exception as err:
        print(f"Error: {err}")