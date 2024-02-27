from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time

# Replace 'your_url_here' with the actual URL you want to scrape
url = 'https://www.cnbc.com/world/?region=world'

# Use a webdriver to interact with the page
driver = webdriver.Chrome()  # Make sure you have the ChromeDriver executable in your PATH

try:
    driver.get(url)
    
    # Wait for dynamic content to load (you might need to adjust the time based on the page)
    time.sleep(5)

    # Get the HTML content after dynamic loading
    html_content = driver.page_source

    # Save the HTML data to a file in the "raw_data" folder
    save_folder = '../data/raw_data'
    os.makedirs(save_folder, exist_ok=True)

    with open(os.path.join(save_folder, 'web_data.html'), 'w', encoding='utf-8') as file:
        file.write(html_content)

    print("HTML data saved to 'raw_data/web_data.html'")
finally:
    driver.quit()