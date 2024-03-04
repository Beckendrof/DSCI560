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
            ADD COLUMN Location VARCHAR(255),
            ADD COLUMN wellname VARCHAR(255)
        """)
        db.commit()
        print("New columns added to data table successfully.")
    except mysql.connector.Error as err:
        print("Error adding new columns to data table:", err)

# Function to insert retrieved data into data table
def insert_into_data_table(cursor, db, closest_city, well_type, well_status, oil_produced, gas_produced, Operator, Location, wellname, well_number):
    try:
        cursor.execute("""
            UPDATE data 
            SET ClosestCity = %s, 
                WellType = %s, 
                WellStatus = %s, 
                OilProduced = %s, 
                GasProduced = %s,
                Operator = %s,
                Location = %s,
                wellname = %s
            WHERE well_number = %s
        """, (closest_city, well_type, well_status, oil_produced, gas_produced, Operator, Location, wellname, well_number))
        db.commit()
        # print("Data inserted successfully into data table.")
    except mysql.connector.Error as err:
        print("Error inserting data into data table:", err)

# Function to search for well information on the website and insert into oil_wells table
def search_and_insert_well_info(cursor, db, api_number=None, well_name=None, well_number=None):
    try:
        # Check if at least one of api_number or well_name is provided
        if api_number or well_name:
            # Open the search page
            driver.get("https://www.drillingedge.com/search")
            
            # Find the input fields for well name and API number
            well_name_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='well_name']"))
            )
            api_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='api_no']"))
            )
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
                wellname = search_results[1].text
                lease_name = search_results[2].text
                location = search_results[3].text
                operator = search_results[4].text
                status = search_results[5].text
                
                # Check if the well name link is clickable (i.e., if there is more information available)
                well_name_link = driver.find_elements(By.LINK_TEXT, wellname)
                if well_name_link:
                    try:
                        well_name_link[0].click()  # Click on the well name link to open the details page
                        # Wait for the details page to load
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.block_stat:nth-of-type(1)")))
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.block_stat:nth-of-type(2)")))
                        
                        # Extract additional information from the details page
                        try:
                            oil_produced_element = driver.find_element(By.CSS_SELECTOR, "p.block_stat:nth-of-type(1)")
                            oil_produced = oil_produced_element.text
                        except NoSuchElementException:
                            oil_produced = "No value found"

                        try:
                            gas_produced_element = driver.find_element(By.CSS_SELECTOR, "p.block_stat:nth-of-type(2)")
                            gas_produced = gas_produced_element.text
                        except NoSuchElementException:
                                gas_produced = "No value found"

                        well_status_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Well Status')]/following-sibling::td")
                        well_type_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Well Type')]/following-sibling::td")
                        township_range_section_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Township Range Section')]/following-sibling::td")
                        county_element = driver.find_element(By.XPATH, "//th[contains(text(), 'County')]/following-sibling::td")
                        closest_city_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Closest City')]/following-sibling::td")
                        
                        #oil_produced = oil_produced_element.text if oil_produced_element else "No value found"
                        #gas_produced = gas_produced_element.text if gas_produced_element else "No value found"
                        well_status = well_status_element.text if well_status_element else "No value found"
                        well_type = well_type_element.text if well_type_element else "No value found"
                        township_range_section = township_range_section_element.text if township_range_section_element else "No value found"
                        county = county_element.text if county_element else "No value found"
                        closest_city = closest_city_element.text if closest_city_element else "No value found"
                        
                        # Insert retrieved data into data table
                        insert_into_data_table(cursor, db, closest_city, well_type, well_status, oil_produced, gas_produced, operator, location, wellname, well_number)
                        
                        # Print the new values
                        # print("New values after insertion:")
                        # print("API:", api)
                        # print("Well Name:", wellname)
                        # print("Lease Name:", lease_name)
                        # print("Location:", location)
                        # print("Operator:", operator)
                        # print("Status:", status)
                        # print("Oil Produced:", oil_produced)
                        # print("Gas Produced:", gas_produced)
                        # print("Well Status:", well_status)
                        # print("Well Type:", well_type)
                        # print("Township Range Section:", township_range_section)
                        # print("County:", county)
                        # print("Closest City:", closest_city)
                        print("Data updated for ", well_name)
                        return True
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Error occurred while retrieving information for API number '{api_number}' and well name '{well_name}'")
                        return False
                else:
                    print(f"No information available for the well '{well_name}'.")
                    return False
        else:
            print("Please provide either the API number or the well name.")
            return False
    except Exception as e:
        print(f"Error occurred for API number '{api_number}' and well name '{well_name}'")
        return False
    finally:
        # Navigate back to the search results page
        driver.back()
        # Wait for the previous page to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.interest_table')))

def scrape():
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
    cursor.execute("SELECT well_number, api, well_name FROM data")
    rows = cursor.fetchall()

    # Set up a count to keep track of successful retrievals
    successful_retrievals = 0

    for row in rows:
        well_number, api_number, well_name = row
        # Search for well information using API number and well name
        if api_number and well_name:
            if not search_and_insert_well_info(cursor, db, api_number, well_name, well_number):
                # If retrieving data with both API number and well name together fails,
                # try fetching the data using only one of them
                print(f"Trying to retrieve data using API number '{api_number}' only...")
                if not search_and_insert_well_info(cursor, db, api_number=api_number, well_number=well_number):
                    print(f"Trying to retrieve data using well name '{well_name}' only...")
                    search_and_insert_well_info(cursor, db, well_name=well_name, well_number=well_number)
        elif api_number:
            search_and_insert_well_info(cursor, db, api_number=api_number, well_number=well_number)
        elif well_name:
            search_and_insert_well_info(cursor, db, well_name=well_name, well_number=well_number)
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
