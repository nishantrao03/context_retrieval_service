# import os
# import re
# from dotenv import load_dotenv
# from llama_parse import LlamaParse

# # --- 1. CONFIGURATION & SETUP ---
# # Calculate the path to the .env file (2 levels up from ingestion/loaders)
# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, '..', '..', '.env')

# # Load the environment variables
# if os.path.exists(env_path):
#     load_dotenv(env_path)
# else:
#     print(f"Warning: .env file not found at {env_path}")

# # Verify API Key
# api_key = os.getenv("LLAMA_CLOUD_API_KEY")
# if not api_key:
#     raise ValueError("LLAMA_CLOUD_API_KEY not found. Please set it in your .env file.")

# # --- 2. CORE LOGIC: MARKDOWN TO JSON CONVERTER ---
# def markdown_to_json_structure(markdown_text):
#     """
#     Parses LlamaParse Markdown output into the specific JSON format:
#     [
#       { "text": "...", "section": "...", "type": "..." },
#       ...
#     ]
#     Handles linearized tables, section tracking, and list identification.
#     """
#     lines = markdown_text.split('\n')
#     chunks = []
#     current_section = "General Context" # Default section if none found
    
#     # Table processing buffer
#     table_buffer = []
#     in_table = False

#     def process_table_buffer(buffer, section_name):
#         """Helper to convert a buffered markdown table into linearized text chunks."""
#         if len(buffer) < 2: return [] # Not a valid table
        
#         # Extract headers (first row)
#         # Remove leading/trailing pipes and split
#         headers = [h.strip() for h in buffer[0].strip().strip('|').split('|')]
        
#         table_chunks = []
#         # Skip index 1 (the separator row like |---|---|)
#         for row in buffer[2:]:
#             if not row.strip(): continue
#             cells = [c.strip() for c in row.strip().strip('|').split('|')]
            
#             # Safety: Ensure cells match headers length
#             if len(cells) != len(headers):
#                 continue 

#             # Linearize: "Header: Value. Header: Value."
#             linearized_text = ""
#             for i, header in enumerate(headers):
#                 val = cells[i] if i < len(cells) else ""
#                 linearized_text += f"{header}: {val}. "
            
#             table_chunks.append({
#                 "text": linearized_text.strip(),
#                 "section": section_name,
#                 "type": "table"
#             })
#         return table_chunks

#     # --- MAIN PARSING LOOP ---
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue

#         # A. Detect Sections (Headers like #, ##, ###)
#         if line.startswith('#'):
#             # If we were in a table, flush it first
#             if in_table:
#                 chunks.extend(process_table_buffer(table_buffer, current_section))
#                 table_buffer = []
#                 in_table = False
            
#             # Clean the header text (remove # and space)
#             current_section = line.lstrip('#').strip()
#             continue

#         # B. Detect Tables (Lines starting with |)
#         if line.startswith('|'):
#             in_table = True
#             table_buffer.append(line)
#             continue
#         else:
#             # If we were in a table but hit a non-table line, process the table
#             if in_table:
#                 chunks.extend(process_table_buffer(table_buffer, current_section))
#                 table_buffer = []
#                 in_table = False

#         # C. Detect Lists (Bullets like *, -)
#         if line.startswith('* ') or line.startswith('- '):
#             clean_text = line[2:].strip()
#             # Inject Context: Prepend section name to list items for better retrieval
#             # (Optional: based on your preference, but usually good for lists)
#             final_text = f"{current_section}: {clean_text}"
            
#             chunks.append({
#                 "text": final_text,
#                 "section": current_section,
#                 "type": "list"
#             })
#             continue

#         # D. Narrative Text
#         chunks.append({
#             "text": line,
#             "section": current_section,
#             "type": "narrative"
#         })

#     # Flush any remaining table at end of file
#     if in_table and table_buffer:
#         chunks.extend(process_table_buffer(table_buffer, current_section))

#     return chunks

# # --- 3. PUBLIC FUNCTION TO CALL ---
# def parse_pdf(file_path):
#     """
#     Main entry point. 
#     1. Uploads PDF to LlamaParse -> Gets Markdown.
#     2. Converts Markdown -> JSON Structure.
#     """
#     print(f"Processing PDF: {file_path}")
    
#     parser = LlamaParse(
#         api_key=api_key,
#         result_type="markdown",  # CRITICAL: Forces layout analysis
#         verbose=True
#     )

#     # LlamaParse returns a list of Document objects
#     documents = parser.load_data(file_path)
    
#     if not documents:
#         print("No content extracted.")
#         return []

#     # Combine all pages into one markdown string
#     full_markdown = "\n".join([doc.text for doc in documents])
    
#     # Debug: Uncomment to see raw markdown if needed
#     # print("DEBUG RAW MARKDOWN:\n", full_markdown)

#     # Convert to your preferred JSON format
#     structured_data = markdown_to_json_structure(full_markdown)
    
#     return structured_data

# # --- 4. TEST EXECUTION (Run this file directly to test) ---
# if __name__ == "__main__":
#     # Point this to your actual file location for testing
#     # Assuming test file is in ingestion/loaders/
#     test_pdf_path = os.path.join(current_dir, 'pdftext.pdf') 
    
#     # Just creating a dummy file path if it doesn't exist for the example to run without crash
#     if not os.path.exists(test_pdf_path):
#         print(f"Test file not found at {test_pdf_path}. Please adjust path in __main__ block.")
#     else:
#         result = parse_pdf(test_pdf_path)
#         import json
        
#         # Write output to pdf_output.txt in the same directory
#         output_path = os.path.join(current_dir, 'pdf_output.txt')
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)
        
#         print(f"Output successfully written to {output_path}")

# pdf_processor.py

# NOTE: This logic is only for PDF files.

import os
import re
from dotenv import load_dotenv
from llama_parse import LlamaParse

# --- 1. CONFIGURATION & SETUP ---
# Calculate the path to the .env file (2 levels up from ingestion/loaders)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '..', '..', '.env')

# Load the environment variables
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

# Verify API Key
api_key = os.getenv("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY not found. Please set it in your .env file.")

# --- 2. CORE LOGIC: MARKDOWN TO JSON CONVERTER ---
def markdown_to_json_structure(markdown_text):
    """
    Parses LlamaParse Markdown output into the specific JSON format:
    [
      { "text": "...", "section": "...", "type": "..." },
      ...
    ]
    Handles linearized tables, section tracking, and list identification.
    """
    lines = markdown_text.split('\n')
    chunks = []
    current_section = "General Context" # Default section if none found
    
    # Table processing buffer
    table_buffer = []
    in_table = False

    def process_table_buffer(buffer, section_name):
        """Helper to convert a buffered markdown table into linearized text chunks."""
        if len(buffer) < 2: return [] # Not a valid table
        
        # Extract headers (first row)
        # Remove leading/trailing pipes and split
        headers = [h.strip() for h in buffer[0].strip().strip('|').split('|')]
        
        table_chunks = []
        # Skip index 1 (the separator row like |---|---|)
        for row in buffer[2:]:
            if not row.strip(): continue
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            
            # Safety: Ensure cells match headers length
            if len(cells) != len(headers):
                continue 

            # Linearize: "Header: Value. Header: Value."
            linearized_text = ""
            for i, header in enumerate(headers):
                val = cells[i] if i < len(cells) else ""
                linearized_text += f"{header}: {val}. "
            
            table_chunks.append({
                "text": linearized_text.strip(),
                "section": section_name,
                "type": "table"
            })
        return table_chunks

    # --- MAIN PARSING LOOP ---
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # A. Detect Sections (Headers like #, ##, ###)
        if line.startswith('#'):
            # If we were in a table, flush it first
            if in_table:
                chunks.extend(process_table_buffer(table_buffer, current_section))
                table_buffer = []
                in_table = False
            
            # Clean the header text (remove # and space)
            current_section = line.lstrip('#').strip()
            continue

        # B. Detect Tables (Lines starting with |)
        if line.startswith('|'):
            in_table = True
            table_buffer.append(line)
            continue
        else:
            # If we were in a table but hit a non-table line, process the table
            if in_table:
                chunks.extend(process_table_buffer(table_buffer, current_section))
                table_buffer = []
                in_table = False

        # C. Detect Lists (Bullets like *, -)
        if line.startswith('* ') or line.startswith('- '):
            clean_text = line[2:].strip()
            # Inject Context: Prepend section name to list items for better retrieval
            # (Optional: based on your preference, but usually good for lists)
            final_text = f"{current_section}: {clean_text}"
            
            chunks.append({
                "text": final_text,
                "section": current_section,
                "type": "list"
            })
            continue

        # D. Narrative Text
        chunks.append({
            "text": line,
            "section": current_section,
            "type": "narrative"
        })

    # Flush any remaining table at end of file
    if in_table and table_buffer:
        chunks.extend(process_table_buffer(table_buffer, current_section))

    return chunks

# --- 3. PUBLIC FUNCTION TO CALL ---
def parse_pdf(file_path):
    """
    Main entry point. 
    1. Uploads PDF to LlamaParse -> Gets Markdown.
    2. Converts Markdown -> JSON Structure.
    """
    print(f"Processing PDF: {file_path}")
    
    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",  # CRITICAL: Forces layout analysis
        verbose=True
    )

    # LlamaParse returns a list of Document objects
    documents = parser.load_data(file_path)
    
    if not documents:
        print("No content extracted.")
        return []

    # Combine all pages into one markdown string
    full_markdown = "\n".join([doc.text for doc in documents])
    
    # Debug: Uncomment to see raw markdown if needed
    # print("DEBUG RAW MARKDOWN:\n", full_markdown)

    # Convert to your preferred JSON format
    structured_data = markdown_to_json_structure(full_markdown)
    
    return structured_data

# # --- 4. TEST EXECUTION (Run this file directly to test) ---
# if __name__ == "__main__":
#     # Point this to your actual file location for testing
#     # Assuming test file is in ingestion/loaders/
#     test_pdf_path = os.path.join(current_dir, 'project_update.pdf') 
    
#     # Just creating a dummy file path if it doesn't exist for the example to run without crash
#     if not os.path.exists(test_pdf_path):
#         print(f"Test file not found at {test_pdf_path}. Please adjust path in __main__ block.")
#     else:
#         result = parse_pdf(test_pdf_path)
#         import json
        
#         # Write output to pdf_output.txt in the same directory
#         output_path = os.path.join(current_dir, 'pdf_output.txt')
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)
        
#         print(f"Output successfully written to {output_path}")