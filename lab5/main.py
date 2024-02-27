from extract import *
import pandas as pd
import os

# Your defined regex patterns
regex_patterns = {
    "api": r"(\d{2}-\d{3}-\d{5})",
    "longitude": r"((\d{1,3})\s*°\s*(\d{1,2})\s*'\s*(\d{1,2}\.\d+)\s*([EW]))",
    "latitude": r"((\d{1,3})\s*°\s*(\d{1,2})\s*'\s*(\d{1,2}\.\d+)\s*([NS]))",
    "well_name": r"([A-Za-z]+(?:\s+[A-Za-z]+)?\s+\d+\s+\d+-\d+\s?+\d+[A-Z]?)",
    "date_stimulated": r"Date Stimulated[^\n]*\n(\d{2}/\d{2}/\d{4}) |Date Stimulated.*(\d{2}/\d{2}/\d{4})",
    "stimulated_formation": r"Stimulated Formation.*\d{2}/\d{2}/\d{4}\s?\n([A-Za-z]+(?:\s+[A-Za-z]+)*) |Stimulated Formation[^\n]*\n([A-Za-z0-9]+(?:\s+[A-Za-z]+))\s[^0-9.]*",
    "top_ft": r"% Top \(Ft\)\s?([0-9]+) |% Top \(Ft\)[^\n]*\n([0-9]+) |Stimulated Formation I[^\n]*\n[^\d]*(\d+)",
    "bottom_ft": r"\d Bottom \(Ft\)[^\n]*\n([0-9]+) |Stimulated Formation I[^\n]*\n[^\d]*\d*\s(\d+)",
    "stimulation_stages": r"Stimulation Stages[^\n]*\n.*\s(\d+)\s* |Stimulated Formation I[^\n]*\n[^\d]*\d*\s\d*\s(\d+)",
    "volume": r"Volume Volume Units[^\n]*\n(\d+) |Stimulated Formation I[^\n]*\n[^\d]*\d*\s\d*\s\d*\s(\d+)",
    "volume_units": r"Volume Volume Units[^\n]*\n\d*\s(\w+) |Stimulated Formation I[^\n]*\n[^\d]*[^A-Za-z]*(.*)\n",
    "acid_percent": r"(?i)Acid %\s*(\d+)",
    "type_treatment": r"type treatment\s\n(.+)\n|Treatment.*\(BBLS/Min\)\s(?!DET)([A-Za-z]+(?:\s+[A-Za-z]+)?)",
    "lbs_proppant": r"Lbs Proppant[^\n]\n(\d+) |lbs proppant[^\d]*(\d+)",
    "max_treatment_pressure": r"Maximum Treatment Pressure \(PSI\) \n(\d+) |Maximum Treatment Pressure \(PSI\)[^\d]*\d+[^\d]*(\d+)",
    "max_treatment_rate": r"Treatment Rate \(BBLS/Min\) \n(\d+\.\d+) |Treatment Rate \(BBLS/Min\)[^\n]*\n(\d+\.\d+)",
}

input_folder = "well_data" #Point to your folder directory containing all the pdfs
output_folder = "well_data_txt"

data_list = []

for filename in os.listdir(output_folder):
    file_path = os.path.join(output_folder, filename)   
    if os.path.isfile(file_path):
        output_file_path = os.path.join(output_folder, f"{filename.split('.')[0]}_processed.csv")
        if os.path.exists(output_file_path):
            print(f"Skipping file {filename} as it has already been processed.")
            continue
        print(f"Processing file: {file_path}")       
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            extracted_data = parse_extracted_text(file_content, regex_patterns)
            extracted_data['file_name'] = filename.split(".")[0]
            data_list.append(extracted_data)

df = pd.DataFrame(data_list)
df.to_csv("well_info.csv")