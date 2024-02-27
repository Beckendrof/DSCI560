from extract import *
from upload import *
from webscraper import *
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
csv_file = "well_info.csv"

data_list = []

while True:
    if os.path.isfile(csv_file): #Commented out for part one. Run individual files.
        # print("Uploading extracted data to database...")
        # upload() 
        # print("Scrapping data from web...")
        # scrape()
        # print("Done.")
        break
    else:
        for filename in os.listdir(input_folder): 
            file = filename.split(".")[0]
            input_file_path = os.path.join(input_folder, filename) 
            output_file_path = os.path.join(output_folder, f"{file}.txt")
            if os.path.isfile(input_file_path):
                if os.path.exists(output_file_path):
                    print(f"Skipping file {filename} as text extraction is complete.")
                    continue
                else:
                    print(f"Extracting Text from {filename}")
                    extracted_text = extract_text_from_pdf(input_file_path)
                    if not extracted_text.strip():
                        print("Using OCR to extract data...")
                        extracted_text = ocr_pdf(input_file_path)
                    base_filename = os.path.splitext(os.path.basename(input_file_path))[0]
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(extracted_text)  
                    print("Done")

        for filename in os.listdir(output_folder): 
            file_path = os.path.join(output_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                print(f"Processing {filename}")
                file_content = file.read()
                extracted_data = parse_extracted_text(file_content, regex_patterns)
                extracted_data['file_name'] = filename.split(".")[0]
                data_list.append(extracted_data)    

        df = pd.DataFrame(data_list)
        df.to_csv("well_info.csv")