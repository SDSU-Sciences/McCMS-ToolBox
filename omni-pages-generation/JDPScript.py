# TO RUN THE SCRIPT
# In root directory: 
#   - add folder "data" -> put excel sheet here
#   - add folder "templates" -> put template-profile.txt here
# Run: python script.py
#
# WARNING: Replace any raw "&" in the sheet with "&amp;" or HTML breaks.

#Change Sheet ID in line 20.
#Change the template name accordingly. 
#Change the folder name inside project folder. Currently it is sesh.

import smartsheet
import pandas as pd
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from datetime import datetime

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

sheet = smartsheet_client.Sheets.get_sheet('c86wqf5x54fvVqCmj77X3cQVFp8FRM62VWg9pj81')
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
def make_safe_filename(name, idx):
    s = "" if name is None else str(name).strip()
    if not s:
        s = f"row-{idx+1}"

    bad_chars = r'<>:"/\\|?*\t'
    s = s.translate({ord(c): "_" for c in bad_chars})
    s = re.sub(r"[ ]{2,}", " ", s)
    s = re.sub(r"_{2,}", "_", s)
    s = s.strip(" .")

    if not s:
        s = f"row-{idx+1}"

    return s

# column MUST be "File Name"
COL = "File Name"
if COL not in df.columns:
    raise KeyError(f'"{COL}" column not found. Available: {list(df.columns)}')

safe_names = [make_safe_filename(v, i) for i, v in enumerate(df[COL].tolist())]

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
template_path = Path("omni-pages-generation/templates/JDPstudentsTemplate.txt")
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
    "Street Address Line 2","City","State","Zip Code","Office Hours","Mail Code","Lab URL",
    "Links","Courses","Student Opportunities","Mentors","Research Area","Accounts",
    "Areas of Expertise","Education","Presentations","Service","Publications","Certifications","Interests"
    "Grants","Clinical Trials","Awards and Honors","Patents and Copyrights",
    "Media","Fun Facts","File Name"
]

for i, row in df.iterrows():

    file_path = subfolder_path / f"{safe_names[i]}.pcf"

    with open(file_path, "w", encoding="utf-8") as file_n:
        modified_template_content = template_file_content

        for column_name in df.columns:

            keyword = f"|||{column_name}|||"
            replace_text = str(row[column_name])

            #CONVERT DECIMAL TO INTEGER (ZIPCODE, MAILCODE, PHONE NUMBER)
            NUMERIC_FIELDS = ["Zip Code", "Mail Code", "Phone Number", "Street Address Line 1", "Street Address Line 2"]

            if column_name in NUMERIC_FIELDS:
                if pd.notnull(replace_text) and replace_text != "":
                    text = str(replace_text).strip()

                    # CASE 1: Entire field is numeric (e.g., "6560.0")
                    if re.fullmatch(r"\d+(\.\d+)?", text):
                        try:
                            text = str(int(float(text)))   # Remove decimals safely
                        except:
                            text = text

                    # CASE 2: Phone number — clean extra characters
                    if column_name == "Phone Number":
                        digits = re.sub(r"\D", "", text)
                        if len(digits) == 10:
                            text = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                        else:
                            text = digits

                    replace_text = text

                else:
                    replace_text = ""

            else:
                replace_text = str(replace_text)
            # CLEAN INLINE HTML
            if "<" in replace_text or ">" in replace_text:
                replace_text = clean_html(replace_text)

            # IF FIELD IS A LIST FIELD
            if column_name in LIST_FIELDS:

                replace_arr = replace_text.split("\n")

                # SPECIAL: EMAIL MUST ALWAYS STAY PLAIN TEXT
                if column_name == "E-mail":
                    replace_text = replace_arr[0] if replace_arr else ""

                # REGULAR FIELDS
                elif len(replace_arr) <= 1:
                    replace_text = replace_arr[0] if replace_arr else ""

                # MULTI-LINE → CONVERT TO <ul>
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

            # REPLACE IN TEMPLATE
            modified_template_content = modified_template_content.replace(keyword, replace_text)

        file_n.write(modified_template_content)

    print(f"Created {df['File Name'][i]}.pcf in {subfolder_name}")
