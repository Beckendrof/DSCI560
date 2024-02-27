import PyPDF2
import re
from pdf2image import convert_from_path
import pytesseract

# Define using PyPDF2 to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                try:
                    text += page.extract_text() if page.extract_text() else ''
                except KeyError:
                    print(f"KeyError encountered while processing {pdf_path}. Skipping page.")
                    continue  # Skip this page
    except Exception as e:
        print(f"An error occurred while reading {pdf_path}: {e}")
    return text

# Function to parse the extracted text
def parse_extracted_text(text, patterns):
    extracted_data = {}

    for key, exp in patterns.items():
        pattern = re.compile(exp, re.IGNORECASE)
        match = pattern.search(text)
        if match:
            # If a match is found, extract and store the data
            temp = match.group(1) or match.group(2) or match.group(3)
            word = temp.strip()
            if '\n' in word:
                extracted_data[key] = word.split('\n')[1]
            else: 
                extracted_data[key] = word
        else:
            # If no match is found, set the value to None
            extracted_data[key] = None

    return extracted_data

# Function to perform OCR on PDF and extract text
def ocr_pdf(pdf_path):
    text = ""
    images = convert_from_path(pdf_path, dpi=300)  # Convert PDF to a list of images
    for image in images:
        text += pytesseract.image_to_string(image)  # Perform OCR on the image
    return text