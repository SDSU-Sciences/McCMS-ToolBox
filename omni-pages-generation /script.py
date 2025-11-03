# TO RUN THE SCRIPT
# In root directory where this script exists, add a folder "data" -> put the excel sheet here
# In root directory where this script exists, add a folder "template" -> put your template txt file here
# run the command "python script.py"

# Note: Make sure there are no single '&' in the excel sheet, as it will break html parsing: Replace `&` with `&amp;` in the excel sheet.


import pandas as pd
import os
from bs4 import BeautifulSoup, Comment
from datetime import datetime

def clean_html(text):
    """
    Cleans the HTML content by removing comments and unnecessary tags.
    """
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove comments
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove script and style elements
    for div in soup.findAll("div"):
        div.unwrap()
        
    for tag in soup.findAll():
        tag.attrs.pop("class", None)
        tag.attrs.pop("style", None)
        
    print("Cleaned html content: ", str(soup))
        
    return str(soup)

# Load the data from the Excel file
data = pd.read_excel('./data/news-pages.xlsx')
file_names = data["File Name"]
print("file names: ", file_names)
data_len = len(data)
data_columns = data.columns

# Replace NaN values with empty string
data = data.fillna('')

# Set up the projects path and subfolder
projects_path = "./projects"
subfolder_name = "./sesh" 
subfolder_path = os.path.join(projects_path, subfolder_name)

# Create the projects and subfolder if they don't exist
if not os.path.exists(subfolder_path):
    os.makedirs(subfolder_path)
    print(f"Folder {subfolder_path} created!")

print("Creating files in projects subfolder")
for i in range(data_len):
    with open("./templates/template-news.txt", "r") as template_file:
        template_file_content = template_file.read()

    # Generate the full file path
    file_path = os.path.join(subfolder_path, file_names[i] + ".pcf")

    with open(file_path, "w") as file_n:
        modified_template_content = template_file_content
        for column_name in data_columns:
            keyword = f"|||{column_name}|||"
            replace_text = str(data[column_name][i])
            # if keyword == "|||Date|||":
            #     print(replace_text)
            #     date_obj = datetime.strptime(replace_text, "%Y-%m-%d %H:%M:%S")
            #     replace_text = date_obj.strftime("%m/%d/%Y %I:%M:%S %p")
            replace_text = clean_html(replace_text)
            if column_name in ["Education", "Awards and Honors", "Courses", "Research", "Clinical Trials", "Grants", "Presentations", "Publications", "Service", "Fun Facts"]:
                replace_arr = replace_text.split("\n")
                if len(replace_arr) > 0:
                    replace_text = "<ul class='dm-profile-activities' style='font-family:proxima-nova, Helvetica, Arial, sans-serif;text-align:left;text-indent:-0.5in;list-style-type:none;margin-left:0in;padding-left:0.5in'>"
                    for item in replace_arr:
                        replace_text += f"<li class='dm-profile-acitivity'>{item}</li>"
                    replace_text += "</ul>"
            modified_template_content = modified_template_content.replace(keyword, replace_text)

        file_n.write(modified_template_content)
    print(f"Created {file_names[i]}.pcf in {subfolder_name}")
