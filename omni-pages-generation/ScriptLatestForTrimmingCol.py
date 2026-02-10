# TO RUN THE SCRIPT
# In root directory: 
#   - add folder "data" -> put excel sheet here
#   - add folder "templates" -> put template-profile.txt here
# Run: python script.py
#
# WARNING: Replace any raw "&" in the sheet with "&amp;" or HTML breaks.

#Change Sheet ID in line 20. Add access token in line 17.
#Change the template name accordingly. 
#Change the folder name inside project folder. Currently it is sesh.

import smartsheet
import pandas as pd
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from typing import Optional, Set

PLACEHOLDER_RE = re.compile(r"\|\|\|([^|]+)\|\|\|")

def remove_unreplaced_placeholders(text: str, keep: Optional[Set[str]] = None) -> str:
    """
    Removes any remaining |||Column Name||| tokens from output.
    If keep is provided, tokens whose inner name is in keep are preserved.
    """
    def _sub(m):
        key = m.group(1).strip()
        if keep and key in keep:
            return m.group(0)
        return ""
    return PLACEHOLDER_RE.sub(_sub, text)

def is_blank(val) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s == "" or s.lower() == "nan"

# ---------------------------------------------------------
# CLEAN HTML
# ---------------------------------------------------------
def clean_html(text):
    soup = BeautifulSoup(text, 'html.parser')

    # Remove comments
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # Remove script/style completely
    for t in soup.find_all(["script", "style"]):
        t.decompose()

    print("Cleaned html content:", str(soup))
    return str(soup)

# ---------------------------------------------------------
# LOAD SMARTSHEET DATA
# ---------------------------------------------------------
smartsheet_client = smartsheet.Smartsheet('v2JfboaYuoy1IMnWR1Fh2XXYXodJXikVOlpel')
sheet = smartsheet_client.Sheets.get_sheet('VxGX9jgQ4vR64FJm4hqM7FVqMwq6wwp3Chfw6j81')

data = []

for row in sheet.rows:
    row_data = {}
    for cell, column in zip(row.cells, sheet.columns):
        row_data[column.title] = cell.value
    data.append(row_data)

df = pd.DataFrame(data)
df = df.fillna('')   # clean NaN

print("Columns in sheet:", list(df.columns))

# ---------------------------------------------------------
# SAFE FILE NAMES
# ---------------------------------------------------------
def make_filename_from_name(first, last, idx):
    first = "" if pd.isna(first) else str(first).strip().lower()
    last = "" if pd.isna(last) else str(last).strip().lower()

    name = f"{first}-{last}".strip("-")

    if not name:
        name = f"row-{idx+1}"

    # Replace spaces with hyphens
    name = re.sub(r"\s+", "-", name)

    # Remove invalid filename characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)

    # Collapse multiple hyphens
    name = re.sub(r"-{2,}", "-", name)

    return name

safe_names = [
    make_filename_from_name(row["First Name"], row["Last Name"], i)
    for i, row in df.iterrows()
]

# handle duplicate names
seen = {}
def dedup(name):
    if name not in seen:
        seen[name] = 0
        return name
    seen[name] += 1
    return f"{name} ({seen[name]})"

safe_names = [dedup(n) for n in safe_names]

# ---------------------------------------------------------
# SETUP OUTPUT FOLDER
# ---------------------------------------------------------
projects_path = Path("./projects")
subfolder_name = "sesh"
subfolder_path = projects_path / subfolder_name
subfolder_path.mkdir(parents=True, exist_ok=True)
print("Writing to:", subfolder_path.resolve())

# load template
template_path = Path("templates/template-test.txt")
template_file_content = template_path.read_text(encoding="utf-8")

# ---------------------------------------------------------
# WRITE INITIAL EMPTY FILES
# ---------------------------------------------------------
for name in safe_names:
    file_path = subfolder_path / f"{name}.pcf"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(template_file_content)
    print("Created:", file_path)

# ---------------------------------------------------------
# MAIN TEMPLATE REPLACEMENT
# ---------------------------------------------------------
LIST_FIELDS = [
    "Primary Column","First Name","Last Name","Display Name","Title","Suffix","Pronouns", "Department",
    "Entry Year","Campus","Partner Instituition","Division","Organizational Unit","Program Area",
    "Bio","E-mail","Phone Number","Building/Location","Street Address Line 1",
    "Street Address Line 2","City","State","Zip Code","Office Hours","Mail Code",
    "Links","Courses","Student Opportunities","Mentors","Research","Accounts",
    "Areas of Specialization","Education","Presentations","Service","Publications","Certifications","Interests",
    "Grants","Clinical Trials","Awards and Honors","Patents and Copyrights",
    "Media","Fun Facts","File Name"
]

sheet_column_titles = set(df.columns)

for i, row in df.iterrows():

    file_path = subfolder_path / f"{safe_names[i]}.pcf"

    with open(file_path, "w", encoding="utf-8") as file_n:
        modified_template_content = template_file_content

        for column_name in df.columns:
            
            keyword = f"|||{column_name}|||"
            raw_val = row[column_name]

            # If blank, replace with "" (so placeholder doesn't remain)
            if is_blank(raw_val):
                modified_template_content = modified_template_content.replace(keyword, "")
                continue

            replace_text = str(raw_val)

            # -------------------------------------------------
            # NEW: SAFELY ESCAPE RAW AMPERSANDS
            # -------------------------------------------------
            # Replace & not already part of an HTML entity
            replace_text = re.sub(r"&(?![a-zA-Z]+;)", "&amp;", replace_text)

            # CONVERT DECIMAL TO INTEGER (ZIPCODE, MAILCODE, PHONE NUMBER)
            NUMERIC_FIELDS = ["Zip Code", "Mail Code", "Phone Number", "Street Address Line 1", "Street Address Line 2"]

            if column_name in NUMERIC_FIELDS:
                text = str(replace_text).strip()

                if re.fullmatch(r"\d+(\.\d+)?", text):
                    try:
                        text = str(int(float(text)))
                    except:
                        pass

                if column_name == "Phone Number":
                    digits = re.sub(r"\D", "", text)
                    if len(digits) == 10:
                        text = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                    else:
                        text = digits

                replace_text = text

            # CLEAN INLINE HTML
            if "<" in replace_text or ">" in replace_text:
                replace_text = clean_html(replace_text)

            # IF FIELD IS A LIST FIELD
            if column_name in LIST_FIELDS:

                replace_arr = [x.strip() for x in replace_text.split("\n") if x.strip()]

                if not replace_arr:
                    replace_text = ""

                elif column_name == "E-mail":
                    replace_text = replace_arr[0]

                elif len(replace_arr) == 1:
                    replace_text = replace_arr[0]

                else:
                    replace_text = (
                        "<ul class='dm-profile-activities' "
                        "style='font-family:proxima-nova, Helvetica, Arial, sans-serif;"
                        "text-align:left;text-indent:-0.5in;list-style-type:none;"
                        "margin-left:0in;padding-left:0.5in'>"
                    )
                    for item in replace_arr:
                        replace_text += f"<li class='dm-profile-acitivity'>{item}</li>"
                    replace_text += "</ul>"

            modified_template_content = modified_template_content.replace(keyword, replace_text)

        # Remove any leftover |||...||| tokens
        modified_template_content = remove_unreplaced_placeholders(modified_template_content)

        file_n.write(modified_template_content)

    print(f"Created {df['File Name'][i]}.pcf in {subfolder_name}")
