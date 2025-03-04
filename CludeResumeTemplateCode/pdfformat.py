import fitz  # PyMuPDF
import json
import os
from collections import defaultdict

def extract_pdf_formatting(file_path):
    formatting_data = {
        "document": {
            "page_count": 0,
            "page_sizes": [],
            "fonts": {},
            "text_blocks": []
        }
    }
    
    # Open the PDF
    doc = fitz.open(file_path)
    formatting_data["document"]["page_count"] = len(doc)
    
    # Extract fonts used in the document
    font_set = set()
    font_counts = defaultdict(int)
    
    for page_num, page in enumerate(doc):
        # Get page dimensions
        formatting_data["document"]["page_sizes"].append({
            "page": page_num + 1,
            "width": page.rect.width,
            "height": page.rect.height
        })
        
        # Extract fonts
        for font in page.get_fonts():
            font_name = font[3]
            font_set.add(font_name)
            font_counts[font_name] += 1
        
        # Extract text blocks with position and formatting
        blocks = page.get_text("dict")["blocks"]
        for i, block in enumerate(blocks):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    span_data = {
                        "page": page_num + 1,
                        "text": span["text"],
                        "font": span["font"],
                        "font_size": span["size"],
                        "color": span["color"],
                        "position": {
                            "x0": span["bbox"][0],
                            "y0": span["bbox"][1],
                            "x1": span["bbox"][2],
                            "y1": span["bbox"][3]
                        },
                        "is_bold": span.get("flags", 0) & 2 > 0,  # Check bold flag
                        "is_italic": span.get("flags", 0) & 4 > 0  # Check italic flag
                    }
                    formatting_data["document"]["text_blocks"].append(span_data)
    
    # Summarize fonts
    for font in font_set:
        formatting_data["document"]["fonts"][font] = {
            "count": font_counts[font],
            "is_common": font_counts[font] > 5  # Consider fonts used more than 5 times as common
        }
    
    return formatting_data

if __name__ == "__main__":
    # Use the specified file path
    resume_path = r"C:\Users\mreev\OneDrive\Desktop\Claude Code\MReeves - Sr Operations Manager - 1.1.25.pdf"
    output_path = "resume_pdf_format_data.json"
    
    try:
        format_data = extract_pdf_formatting(resume_path)
        
        # Save to JSON file
        with open(output_path, 'w') as f:
            json.dump(format_data, f, indent=2)
        
        print(f"PDF formatting data saved to {output_path}")
    except Exception as e:
        print(f"Error extracting PDF formatting: {e}")