import mysql.connector
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up Chrome webdriver with options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = Chrome(service=Service(), options=options)

# Function to add new columns to the data table
def add_columns_to_data_table(cursor, db):
    try:
        cursor.execute("""
            ALTER TABLE data
            ADD COLUMN ClosestCity VARCHAR(255),
            ADD COLUMN WellType VARCHAR(255),
            ADD COLUMN WellStatus VARCHAR(255),
            ADD COLUMN OilProduced VARCHAR(255),
            ADD COLUMN GasProduced VARCHAR(255),
            ADD COLUMN Operator VARCHAR(255),
            ADD COLUMN Location VARCHAR(255)
        """)
        db.commit()
        print("New columns added to data table successfully.")
    except mysql.connector.Error as err:
        print("Error adding new columns to data table:", err)
# Add new columns to the data table if not already added


# Function to insert retrieved data into data table
def insert_into_data_table(cursor, db, closest_city, well_type, well_status, oil_produced, gas_produced,Operator,Location):
    try:
        cursor.execute("""
            UPDATE data 
            SET ClosestCity = %s, 
                WellType = %s, 
                WellStatus = %s, 
                OilProduced = %s, 
                GasProduced = %s,
                Operator=%s,
                Location=%s
        """, (closest_city, well_type, well_status, oil_produced, gas_produced,Operator,Location))
        db.commit()
        print("Data inserted successfully into data table.")
    except mysql.connector.Error as err:
        print("Error inserting data into data table:", err)


# Function to search for well information on the website and insert into oil_wells table
def search_and_insert_well_info(cursor, db, api_number=None, well_name=None):
    try:
        # Check if at least one of api_number or well_name is provided
        if api_number or well_name:
            # Open the search page
            driver.get("https://www.drillingedge.com/search")
            
            # Find the input fields for well name and API number
            well_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='well_name']")
            api_input = driver.find_element(By.CSS_SELECTOR, "input[name='api_no']")
            
            # Fill out the input fields based on provided parameters
            if well_name:
                well_name_input.send_keys(well_name)
            if api_number:
                api_input.send_keys(api_number)
            
            # Submit the search query
            api_input.send_keys(Keys.RETURN)
            
            # Wait for the search results to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.interest_table')))
            
            # Check if there are search results
            no_results_message = driver.find_elements(By.XPATH, "//td[contains(text(), 'Sorry, No Results Returned')]")
            if no_results_message:
                print(f"No results found for the API number '{api_number}' and well name '{well_name}'.")
                return False
            else:
                # Extract relevant information from search results
                search_results = driver.find_elements(By.CSS_SELECTOR, 'table.interest_table td')
                if len(search_results) < 6:
                    print(f"Error: Insufficient data in search results for API number '{api_number}' and well name '{well_name}'.")
                    return False
                
                api = search_results[0].text
                well_name = search_results[1].text
                lease_name = search_results[2].text
                location = search_results[3].text
                operator = search_results[4].text
                status = search_results[5].text
                
                # Check if the well name link is clickable (i.e., if there is more information available)
                well_name_link = driver.find_elements(By.LINK_TEXT, well_name)
                if well_name_link:
                    try:
                        well_name_link[0].click()  # Click on the well name link to open the details page
                        # Wait for the details page to load
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.block_stat:nth-of-type(1)")))
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.block_stat:nth-of-type(2)")))
                        
                        # Extract additional information from the details page
                        oil_produced = driver.find_element(By.CSS_SELECTOR, "p.block_stat:nth-of-type(1)").text
                        gas_produced = driver.find_element(By.CSS_SELECTOR, "p.block_stat:nth-of-type(2)").text
                        well_status = driver.find_element(By.XPATH, "//th[contains(text(), 'Well Status')]/following-sibling::td").text
                        well_type = driver.find_element(By.XPATH, "//th[contains(text(), 'Well Type')]/following-sibling::td").text
                        township_range_section = driver.find_element(By.XPATH, "//th[contains(text(), 'Township Range Section')]/following-sibling::td").text
                        county = driver.find_element(By.XPATH, "//th[contains(text(), 'County')]/following-sibling::td").text
                        closest_city = driver.find_element(By.XPATH, "//th[contains(text(), 'Closest City')]/following-sibling::td").text
                        
                        insert_into_data_table(cursor, db, closest_city, well_type, well_status, oil_produced, gas_produced, operator, location)
                        driver.back()  # Go back to the search results page
                        # Wait for the previous page to load
                        wait = WebDriverWait(driver, 10)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.interest_table')))
                        
                        return True
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Error occurred while retrieving information for API number '{api_number}' and well name '{well_name}': {e}")
                        return False
                else:
                    print(f"No information available for the well '{well_name}'.")
                    return False
        else:
            print("Please provide either the API number or the well name.")
            return False
    except Exception as e:
        print(f"Error occurred for API number '{api_number}' and well name '{well_name}': {e}")
        return False



# def scrape():
#     # Connect to MySQL database
#     db = mysql.connector.connect(
#                 host="localhost",
#                 user="raydiant_user",
#                 password="StrongPassword123!",
#                 database="raydiant"
#             )
#     cursor = db.cursor()


#     add_columns_to_data_table(cursor, db)

#     # Retrieve API number and well name from the MySQL table named 'data'
#     cursor.execute("SELECT api, well_name FROM data")
#     rows = cursor.fetchall()

#     # Set up a count to keep track of successful retrievals
#     successful_retrievals = 0


#     for row in rows:
#         api_number, well_name = row
#         # Search for well information using API number and well name
#         if api_number and well_name:
#             if not search_and_insert_well_info(cursor, db, api_number, well_name):
#                 # If retrieving data with both API number and well name together fails,
#                 # try fetching the data using only one of them
#                 print(f"Trying to retrieve data using API number '{api_number}' only...")
#                 if not search_and_insert_well_info(cursor, db, api_number):
#                     print(f"Trying to retrieve data using well name '{well_name}' only...")
#                     search_and_insert_well_info(cursor, db, well_name)
#         elif api_number:
#             search_and_insert_well_info(cursor, db, api_number)
#         elif well_name:
#             search_and_insert_well_info(cursor, db, well_name)
#         else:
#             print("No API number or well name provided for this entry.")

#     # Select all data from the data table
#     cursor.execute("SELECT * FROM data")
#     rows = cursor.fetchall()

#     # Define the path to the CSV file
#     csv_file_path = "data_table.csv"

#     # Write the data to the CSV file
#     with open(csv_file_path, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         # Write the header row
#         writer.writerow([i[0] for i in cursor.description])
#         # Write the data rows
#         writer.writerows(rows)

#     print(f"Data exported to '{csv_file_path}' successfully.")
#     # Close database connection
#     cursor.close()
#     db.close()


    # Connect to MySQL database
    
db = mysql.connector.connect(
            host="localhost",
            user="raydiant_user",
            password="StrongPassword123!",
            database="raydiant"
        )
cursor = db.cursor()


add_columns_to_data_table(cursor, db)

# Retrieve API number and well name from the MySQL table named 'data'
cursor.execute("SELECT api, well_name FROM data")
rows = cursor.fetchall()

# Set up a count to keep track of successful retrievals
successful_retrievals = 0


for row in rows:
    api_number, well_name = row
    # Search for well information using API number and well name
    if api_number and well_name:
        if not search_and_insert_well_info(cursor, db, api_number, well_name):
            # If retrieving data with both API number and well name together fails,
            # try fetching the data using only one of them
            print(f"Trying to retrieve data using API number '{api_number}' only...")
            if not search_and_insert_well_info(cursor, db, api_number):
                print(f"Trying to retrieve data using well name '{well_name}' only...")
                search_and_insert_well_info(cursor, db, well_name)
    elif api_number:
        search_and_insert_well_info(cursor, db, api_number)
    elif well_name:
        search_and_insert_well_info(cursor, db, well_name)
    else:
        print("No API number or well name provided for this entry.")

# Select all data from the data table
cursor.execute("SELECT * FROM data")
rows = cursor.fetchall()

# Define the path to the CSV file
csv_file_path = "data_table.csv"

# Write the data to the CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow([i[0] for i in cursor.description])
    # Write the data rows
    writer.writerows(rows)

print(f"Data exported to '{csv_file_path}' successfully.")
# Close database connection
cursor.close()
db.close()