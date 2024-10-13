import json
import re
import fitz  # PyMuPDF


def pdf_to_json(pdf_file_path):
    # Dictionary to store the structured content
    content = {}
    
    # Variables to track current section and subheading
    current_section = "Introduction"
    content[current_section] = []
    current_subheading = None

    # Keywords to detect sections
    section_keywords = ["EDUCATION", "WORK EXPERIENCE", "RESEARCH", "PROJECTS", "LEADERSHIP", "CERTIFICATES", "SKILLS"]

    # Create a pattern to detect section headers
    section_pattern = re.compile(r'\b(?:' + '|'.join(section_keywords) + r')\b', re.IGNORECASE)

    pdf_document = fitz.open(pdf_file_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")['blocks']

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span['text'].strip()

                    # Skip empty lines
                    if not text:
                        continue

                    # Detect bold text to use as subheading (optional)
                    is_bold = 'bold' in span['font']

                    # Check if the line contains a section keyword
                    section_match = section_pattern.search(text)

                    if section_match:
                        # Handle content before the section keyword (if mixed content on the same line)
                        if section_match.start() > 0:
                            before_section = text[:section_match.start()].strip()
                            if before_section:
                                if current_subheading:
                                    content[current_section][-1][current_subheading].append(before_section)
                                else:
                                    content[current_section].append(before_section)

                        # Set the new section as the detected section header
                        current_section = text[section_match.start():].strip()
                        content[current_section] = []  # Initialize a new list for the section
                        current_subheading = None  # Reset subheading
                    elif is_bold or text.startswith("Class"):  # Detect either bold text or Class-based subheadings
                        # If bold text or a Class line is detected, treat it as a subheading
                        current_subheading = text
                        content[current_section].append({current_subheading: []})
                    else:
                        # Append the text to the current section or subheading
                        if current_subheading:
                            # Add to the current subheading (it's a dictionary entry in the list)
                            content[current_section][-1][current_subheading].append(text)
                        else:
                            # Append to the section directly
                            content[current_section].append(text)

    # Convert the structured data to JSON format and return it
    return json.dumps(content, ensure_ascii=False, indent=4)



