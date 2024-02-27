import mysql.connector
import pandas as pd
import numpy as np


def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="raydiant_user",
            password="StrongPassword123!",
            database="raydiant"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None



def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS data ("
                       "well_number VARCHAR(255) PRIMARY KEY,"
                       "api VARCHAR(255),"
                       "longitude VARCHAR(255),"
                       "latitude VARCHAR(255),"
                       "well_name VARCHAR(255),"
                       "date_stimulated DATE,"
                       "stimulated_formation VARCHAR(255),"
                       "top_ft VARCHAR(255),"
                       "bottom_ft VARCHAR(255),"
                       "stimulation_stages VARCHAR(255),"
                       "volume VARCHAR(255),"
                       "volume_units VARCHAR(255),"
                       "acid_percent VARCHAR(255),"
                       "type_treatment VARCHAR(10000),"
                       "lbs_proppant VARCHAR(255),"
                       "max_treatment_pressure VARCHAR(255),"
                       "max_treatment_rate VARCHAR(255))"
                       
                       )

        connection.commit()
        print("Table 'data' created successfully")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")

from datetime import datetime

def insert_data(connection, df):
    try:
        cursor = connection.cursor()
        for index, row in df.iterrows():
            # Check if either 'well_name' or 'api' is not null
            if pd.notna(row['well_name']) or pd.notna(row['api']):
                # Handle date format conversion
                date_stimulated = None
                if pd.notna(row['date_stimulated']):
                    date_stimulated = datetime.strptime(row['date_stimulated'], '%m/%d/%Y').strftime('%Y-%m-%d')
                
                # Handle NaN values by checking each column individually
                api = row['api'] if pd.notna(row['api']) else None
                longitude = row['longitude'] if pd.notna(row['longitude']) else 'No Value Found'
                latitude = row['latitude'] if pd.notna(row['latitude']) else 'No Value Found'
                well_name = row['well_name'] if pd.notna(row['well_name']) else None
                stimulated_formation = row['stimulated_formation'] if pd.notna(row['stimulated_formation']) else 'No Value Found'
                top_ft = row['top_ft'] if pd.notna(row['top_ft']) else 'No Value Found'
                bottom_ft = row['bottom_ft'] if pd.notna(row['bottom_ft']) else 'No Value Found'
                stimulation_stages = row['stimulation_stages'] if pd.notna(row['stimulation_stages']) else 'No Value Found'
                volume = row['volume'] if pd.notna(row['volume']) else 'No Value Found'
                volume_units = row['volume_units'] if pd.notna(row['volume_units']) else 'No Value Found'
                acid_percent = row['acid_percent'] if pd.notna(row['acid_percent']) else None
                type_treatment=row['type_treatment'] if pd.notna(row['type_treatment']) else 'No Value Found'
                lbs_proppant = row['lbs_proppant'] if pd.notna(row['lbs_proppant']) else 'No Value Found'
                max_treatment_pressure = row['max_treatment_pressure'] if pd.notna(row['max_treatment_pressure']) else 'No Value Found'
                max_treatment_rate = row['max_treatment_rate'] if pd.notna(row['max_treatment_rate']) else 'No Value Found'
                well_number = row['file_name'] if pd.notna(row['file_name']) else 'No Value Found'
                
                
                api = None if pd.isna(api) else api
                longitude = None if pd.isna(longitude) else longitude
                latitude = None if pd.isna(latitude) else latitude
                well_name = None if pd.isna(well_name) else well_name
                stimulated_formation = None if pd.isna(stimulated_formation) else stimulated_formation
                top_ft = None if pd.isna(top_ft) else top_ft
                bottom_ft = None if pd.isna(bottom_ft) else bottom_ft
                stimulation_stages = None if pd.isna(stimulation_stages) else stimulation_stages
                volume = None if pd.isna(volume) else volume
                volume_units = None if pd.isna(volume_units) else volume_units
                acid_percent = None if pd.isna(acid_percent) else acid_percent
                type_treatment = None if pd.isna(type_treatment) else type_treatment
                lbs_proppant = None if pd.isna(lbs_proppant) else lbs_proppant
                max_treatment_pressure = None if pd.isna(max_treatment_pressure) else max_treatment_pressure
                max_treatment_rate = None if pd.isna(max_treatment_rate) else max_treatment_rate
                well_number = None if pd.isna(well_number) else well_number

                cursor.execute("INSERT INTO data (well_number,api, longitude, latitude, well_name, date_stimulated, "
                               "stimulated_formation, top_ft, bottom_ft, stimulation_stages, volume,volume_units, "
                               "acid_percent, type_treatment,lbs_proppant, max_treatment_pressure, max_treatment_rate) "
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
                               (well_number,api, longitude, latitude, well_name, date_stimulated,
                                stimulated_formation, top_ft, bottom_ft, stimulation_stages,
                                volume,volume_units, acid_percent,type_treatment, lbs_proppant,
                                max_treatment_pressure, max_treatment_rate))
        connection.commit()
        print("Data inserted into MySQL table")
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")

# def upload():
#     df=pd.read_csv('well_info.csv')
#     # Connect to MySQL
#     connection = connect_to_mysql()

#     if connection:
#         # Create table if it doesn't exist
#         create_table(connection)

#         # Insert data into table
#         insert_data(connection, df)

#         # Close connection
#         connection.close()

if __name__ == "__main__":
    df=pd.read_csv('well_info.csv')
    # Connect to MySQL
    connection = connect_to_mysql()

    if connection:
        # Create table if it doesn't exist
        create_table(connection)

        # Insert data into table
        insert_data(connection, df)

        # Close connection
        connection.close()
