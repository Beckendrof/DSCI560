import requests
from bs4 import BeautifulSoup
import csv
import pdfplumber
import pandas as pd

def format_search_query(query):
    # Replace empty spaces with %20
    return query.replace(' ', '%20')

def scrape_subreddit(subreddit_name, search_query):
    try:
        # Format the search query
        formatted_query = format_search_query(search_query)

        # URL of the subreddit
        url = f'https://www.reddit.com/r/{subreddit_name}/search/?q={formatted_query}&restrict_sr=1&type=comment'

        # Send a GET request
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        # Check if the request was successful
        if response.status_code == 200:
            print(f"\nScrapping {search_query} related posts on r/{subreddit_name}...")
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract post title
            post_title = soup.find_all('span', class_='text-16')
            titles = [span.text.strip() for span in post_title]



            # Extract comment content
            comment_content = soup.find_all('div', class_='max-h-[260px] overflow-hidden text-ellipsis text-neutral-content-strong hover:no-underline no-underline no-visited')
            comments = [span.text.strip() for span in comment_content]

            comments = [comment.replace('\n', '') for comment in comments]
            data = list(zip(titles, comments))

            # Specify the CSV file path
            csv_file_path = 'reddit.csv'

            print("Saving relevent post data to csv...")
            # Write data to the CSV file
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)

                # Write header (optional)
                csv_writer.writerow(['Title', 'Comment'])

                # Write data
                csv_writer.writerows(data)

            print("CSV file created")
            print("")
        else:
            print(f"Error: Unable to fetch data. Status code {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

pdf_file_path = "32415.pdf"

#extract text from pdf file - read the file and print the first page on terminal
def scrape_pdf(pdf_file_path):
  print("\nRetrieving data from pdf file....")
  with pdfplumber.open(pdf_file_path) as pdf:
    for page_num in range(len(pdf.pages)):
      page = pdf.pages[page_num]
      page_content = page.extract_text()
      #print(page)
      #print(page_content)

      #print only the 1st page on terminal
      if page_num == 0:
        print(page)
        print("\n")
        print(page_content)
        print("\n")

  pdf.close()

def basic_operations(csv_file_path):
    print("\nRetrieving data from csv file....")
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path, sep=';')
    print("")

    # Display the first few records
    print(df.head())

    # Calculate the size and dimensions of the dataset
    dimensions = df.shape
    print(f"Dimensions of the dataset: {dimensions}")

    # Identify missing data
    missing_data = df.isnull().sum()
    print(missing_data)

    # Additional basic statistics
    print(df.describe())

# Replace 'your_csv_file.csv' with the actual path to your CSV file
csv_file_path = 'student-mat.csv'
if __name__ == "__main__":
  print("1. CSV data")
  print("1. ASCII data from QnA forum")
  print("3. PDF - text data\n")
  choice = int(input("Enter your choice\n"))

  if choice == 1:
    basic_operations(csv_file_path)
  elif choice == 2:
    scrape_subreddit('USC', "CSCI 570")
  elif choice == 3:
    scrape_pdf(pdf_file_path)