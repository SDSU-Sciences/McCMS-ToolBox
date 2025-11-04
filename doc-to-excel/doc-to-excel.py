import os
from docx import Document
import pandas as pd

def parse_docx_to_dicts(file_path):
    doc = Document(file_path)
    entries = []
    current_lines = []

    # Split document by paragraphs with exact text "Image"
    for para in doc.paragraphs:
        text = para.text.strip()
        if text == "Image":
            if current_lines:
                entries.append(current_lines)
            current_lines = []
        else:
            if text != "":
                current_lines.append(text)
    if current_lines:
        entries.append(current_lines)

    data_list = []
    for lines in entries:
        data = {
            "Name": "",
            "Pronouns": "",
            "Bio": "",
            "Email": "",
            "Phone": "",
            "Office": "",
            "Location": "",
            "Education": "",
            "Publications": "",
            "Grants": "",
            "Awards and Honors": ""
        }

        # Temp variables for multiline capture
        current_field = None
        multiline_buffers = {
            "Bio": [],
            "Education": [],
            "Publications": [],
            "Grants": [],
            "Awards and Honors": []
        }

        for line in lines:
            lower = line.lower()

            # Single line fields by keyword
            if "@" in line and "email" not in line.lower():
                # Likely an email address line
                data["Email"] = line.strip()
                current_field = None
            elif lower.startswith("email"):
                # Line like "Email: abc@xyz"
                parts = line.split(":", 1)
                if len(parts) > 1:
                    data["Email"] = parts[1].strip()
                current_field = None
            elif lower.startswith("phone"):
                parts = line.split(" ", 1)
                if len(parts) > 1:
                    data["Phone"] = parts[1].strip()
                current_field = None
            elif lower.startswith("office"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    data["Office"] = parts[1].strip()
                current_field = None
            elif lower.startswith("location"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    data["Location"] = parts[1].strip()
                current_field = None
            elif lower.startswith("pronouns"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    data["Pronouns"] = parts[1].strip()
                current_field = None

            # Multiline section start keywords
            elif lower == "bio":
                current_field = "Bio"
            elif lower == "education":
                current_field = "Education"
            elif lower == "publications":
                current_field = "Publications"
            elif lower == "grants":
                current_field = "Grants"
            elif lower in ["awards & honors", "awards and honors"]:
                current_field = "Awards and Honors"

            # Detect name line (usually first line or line containing academic titles)
            elif data["Name"] == "" and (
                any(t in line for t in ["PH.D.", "Ph.D.", "Professor", "Lecturer", "Dr.", "Assistant Professor"])
                or "," in line  # a common pattern for last name, first name
            ):
                data["Name"] = line.strip()
                current_field = None

            # Add lines to multiline buffers
            else:
                if current_field in multiline_buffers:
                    multiline_buffers[current_field].append(line.strip())
                else:
                    # Lines that don't belong anywhere are ignored or could be logged if needed
                    pass

        # Join multiline fields with line breaks for Excel
        for key in multiline_buffers:
            data[key] = "\n".join(multiline_buffers[key]).strip()

        data_list.append(data)

    return data_list


# Paths
docx_path = r"D:/SDSU/SciDev/Chem Profile Pages.docx"
excel_output = r"D:/SDSU/SciDev/parsed_profiles_clean.xlsx"

# Parse DOCX
parsed = parse_docx_to_dicts(docx_path)

# Convert to DataFrame
df = pd.DataFrame(parsed)

# Save to Excel
df.to_excel(excel_output, index=False)

print(f"Successfully extracted and saved data to:\n{excel_output}")
.