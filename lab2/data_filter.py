import os
import csv
from bs4 import BeautifulSoup

# Create a directory for processed data if it doesn't exist
processed_folder = 'processed_data'
os.makedirs(processed_folder, exist_ok=True)

# Read the HTML file into a Python list
html_file_path = '../data/raw_data/web_data.html'
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the market data container
market_data_container = soup.find('div', class_='MarketsBanner-marketData')

# Extracting market card symbol, stock position, and change percentage
if market_data_container:
    market_data = []

    # Iterate through each 'a' tag inside 'market_data_container'
    for market_card_container in market_data_container.find_all('a', class_='MarketCard-container'):
        market_card_symbol = market_card_container.find('span', class_='MarketCard-symbol').text.strip()
        market_card_stock_position = market_card_container.find('span', class_='MarketCard-stockPosition').text.strip()
        market_card_change_pct = market_card_container.find('span', class_='MarketCard-changesPct').text.strip()

        market_data.append((market_card_symbol, market_card_stock_position, market_card_change_pct))

# Extract data from the Latest News section
news_data = []
news_elements = soup.find_all('li', class_='LatestNews-item')
for news_entry in news_elements:
    timestamp = news_entry.find('time', class_='LatestNews-timestamp').text.strip()
    title = news_entry.find('a', class_='LatestNews-headline').text.strip()
    link = news_entry.find('a', class_='LatestNews-headline').get('href')

    news_data.append((timestamp, title, link))

# Store market data in CSV
market_csv_path = os.path.join(processed_folder, 'market_data.csv')
with open(market_csv_path, 'w', newline='', encoding='utf-8') as market_csv:
    market_writer = csv.writer(market_csv)
    market_writer.writerow(['Symbol', 'Stock Position', 'Changes Pct'])
    market_writer.writerows(market_data)

# Store news data in CSV
news_csv_path = os.path.join(processed_folder, 'news_data.csv')
with open(news_csv_path, 'w', newline='', encoding='utf-8') as news_csv:
    news_writer = csv.writer(news_csv)
    news_writer.writerow(['Timestamp', 'Title', 'Link'])
    news_writer.writerows(news_data)

# Print appropriate messages to the console
print("Filtering fields...")
print(f"Storing Market data in {market_csv_path}")
print(f"Storing News data in {news_csv_path}")
print("CSV files created.")
