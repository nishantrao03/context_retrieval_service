# import json
# from typing import List, Dict, Any, Optional
# from bs4 import BeautifulSoup


# def normalize_unstructured_output(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Normalize unstructured output into embedding-ready text blocks.
#     """

#     normalized: List[Dict[str, Any]] = []
#     current_section: Optional[str] = None

#     for el in elements:
#         el_type = el.get("type")
#         text = (el.get("text") or "").strip()
#         metadata = el.get("metadata", {})

#         if not text:
#             continue

#         if el_type == "Title":
#             current_section = text
#             continue

#         if el_type == "NarrativeText":
#             normalized.append({
#                 "text": text,
#                 "section": current_section,
#                 "type": "narrative"
#             })

#         elif el_type == "ListItem":
#             combined = f"{current_section}: {text}" if current_section else text
#             normalized.append({
#                 "text": combined,
#                 "section": current_section,
#                 "type": "list"
#             })

#         elif el_type == "Table":
#             html = metadata.get("text_as_html")
#             if not html:
#                 continue

#             soup = BeautifulSoup(html, "html.parser")
#             rows = soup.find_all("tr")

#             if len(rows) < 2:
#                 continue

#             headers = [cell.get_text(strip=True) for cell in rows[0].find_all("td")]

#             for row in rows[1:]:
#                 cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
#                 if len(cells) != len(headers):
#                     continue

#                 sentence = ". ".join(
#                     f"{headers[i]}: {cells[i]}" for i in range(len(headers))
#                 ) + "."

#                 normalized.append({
#                     "text": sentence,
#                     "section": current_section,
#                     "type": "table"
#                 })

#     return normalized


# # ---------------- TEMP TEST ----------------
# if __name__ == "__main__":
#     # Read unstructured output from temp.txt
#     with open("temp.txt", "r", encoding="utf-8") as f:
#         unstructured_output = json.load(f)

#     normalized_output = normalize_unstructured_output(unstructured_output)

#     # NEW: write normalized output to final_output.txt
#     with open("output_layer_1.txt", "w", encoding="utf-8") as f:
#         json.dump(normalized_output, f, indent=2, ensure_ascii=False)

#     print(f"Normalized blocks written: {len(normalized_output)}")
#     print("Output saved to final_output.txt\n")

#     # Optional preview
#     for i, item in enumerate(normalized_output[:5], start=1):
#         print(f"--- Block {i} ---")
#         print(f"Section: {item['section']}")
#         print(f"Type: {item['type']}")
#         print(f"Text: {item['text']}\n")

# Version 2

# import json
# from typing import List, Dict, Any, Optional
# from bs4 import BeautifulSoup


# def normalize_unstructured_output(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Normalize unstructured output into embedding-ready text blocks.
#     """

#     normalized: List[Dict[str, Any]] = []
#     current_section: Optional[str] = None

#     for el in elements:
#         el_type = el.get("type")
#         text = (el.get("text") or "").strip()
#         metadata = el.get("metadata", {})

#         if not text:
#             continue

#         if el_type == "Title":
#             current_section = text
#             continue

#         if el_type == "NarrativeText":
#             normalized.append({
#                 "text": text,
#                 "section": current_section,
#                 "type": "narrative"
#             })

#         elif el_type == "ListItem":
#             combined = f"{current_section}: {text}" if current_section else text
#             normalized.append({
#                 "text": combined,
#                 "section": current_section,
#                 "type": "list"
#             })

#         elif el_type == "Table":
#             html = metadata.get("text_as_html")
#             if not html:
#                 continue

#             soup = BeautifulSoup(html, "html.parser")
#             rows = soup.find_all("tr")

#             if len(rows) < 2:
#                 continue

#             headers = [cell.get_text(strip=True) for cell in rows[0].find_all("td")]

#             for row in rows[1:]:
#                 cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
#                 if len(cells) != len(headers):
#                     continue

#                 sentence = ". ".join(
#                     f"{headers[i]}: {cells[i]}" for i in range(len(headers))
#                 ) + "."

#                 normalized.append({
#                     "text": sentence,
#                     "section": current_section,
#                     "type": "table"
#                 })

#     return normalized


# # ---------------- TEMP TEST ----------------
# # if __name__ == "__main__":
# #     # Read unstructured output from temp.txt
# #     with open("temp.txt", "r", encoding="utf-8") as f:
# #         unstructured_output = json.load(f)

# #     normalized_output = normalize_unstructured_output(unstructured_output)

# #     # NEW: write normalized output to final_output.txt
# #     with open("output_layer_1.txt", "w", encoding="utf-8") as f:
# #         json.dump(normalized_output, f, indent=2, ensure_ascii=False)

# #     print(f"Normalized blocks written: {len(normalized_output)}")
# #     print("Output saved to final_output.txt\n")

# #     # Optional preview
# #     for i, item in enumerate(normalized_output[:5], start=1):
# #         print(f"--- Block {i} ---")
# #         print(f"Section: {item['section']}")
# #         print(f"Type: {item['type']}")
# #         print(f"Text: {item['text']}\n")

# Version 3 

# ingestion/loaders/rule_based_normalization.py

import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


def normalize_unstructured_output(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize unstructured output into embedding-ready text blocks.
    """

    normalized: List[Dict[str, Any]] = []
    current_section: str = "General Context"

    for el in elements:
        # Default to UncategorizedText if type is missing to prevent errors
        el_type = str(el.get("type", "UncategorizedText"))
        text = (el.get("text") or "").strip()
        metadata = el.get("metadata", {})

        if not text:
            continue

        # 1. Determine if this element acts as a section heading
        is_heading = False
        
        # Condition A: It is explicitly recognized as a heading by the library
        if el_type in ["Title", "Header"] or el_type.startswith("Heading"):
            is_heading = True
        # Condition B: It is UncategorizedText but structurally looks like a heading
        # (e.g., "1. The Art of Batting" - short, no ending punctuation)
        elif el_type == "UncategorizedText" and len(text) < 60 and not text.endswith('.'):
            is_heading = True

        if is_heading:
            current_section = text
            continue

        # 2. Process Tables
        if el_type == "Table":
            html = metadata.get("text_as_html")
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr")

            if len(rows) < 2:
                continue

            headers = [cell.get_text(strip=True) for cell in rows[0].find_all("td")]

            for row in rows[1:]:
                cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
                if len(cells) != len(headers):
                    continue

                sentence = ". ".join(
                    f"{headers[i]}: {cells[i]}" for i in range(len(headers))
                ) + "."

                normalized.append({
                    "text": sentence,
                    "section": current_section,
                    "type": "table"
                })
            continue

        # 3. Process Lists
        if el_type == "ListItem":
            combined = f"{current_section}: {text}" if current_section != "General Context" else text
            normalized.append({
                "text": combined,
                "section": current_section,
                "type": "list"
            })
            continue

        # 4. Catch-all for NarrativeText and any unrecognized elements
        # This prevents any text from being deleted or lost if unstructured mislabels it.
        normalized.append({
            "text": text,
            "section": current_section,
            "type": "narrative"
        })

    return normalized


# ---------------- TEMP TEST ----------------
# if __name__ == "__main__":
#     # Read unstructured output from temp.txt
#     with open("temp.txt", "r", encoding="utf-8") as f:
#         unstructured_output = json.load(f)

#     normalized_output = normalize_unstructured_output(unstructured_output)

#     # NEW: write normalized output to final_output.txt
#     with open("output_layer_1.txt", "w", encoding="utf-8") as f:
#         json.dump(normalized_output, f, indent=2, ensure_ascii=False)

#     print(f"Normalized blocks written: {len(normalized_output)}")
#     print("Output saved to final_output.txt\n")

#     # Optional preview
#     for i, item in enumerate(normalized_output[:5], start=1):
#         print(f"--- Block {i} ---")
#         print(f"Section: {item['section']}")
#         print(f"Type: {item['type']}")
#         print(f"Text: {item['text']}\n")