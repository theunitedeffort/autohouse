import requests
import json
import pandas as pd

# Load the Excel spreadsheet
excel_file = "client_info.xlsx"  # Change to your file path
df = pd.read_excel(excel_file)

# Base URL
base_url = "https://www.theunitedeffort.org/data/housing/affordable-housing/filter?"

# Function to make GET request and parse JSON ZN     z
def get_apartments(params):
    response = requests.get(base_url + params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
        raise SystemExit(requests.exceptions.ConnectionError)
        return None

# Iterate through each row in the dataframe
for index, row in df.iterrows():
    client_name = row['Client Name']
    preferred_locations = row['Preferred Location']
    type_of_units = row['Type of Unit']
    
    rent = row['Rent']
    income = row['Income']
    
    # Construct query parameters
    query_params = {
        "city": preferred_locations,
        "unittype": type_of_units,
        "available": "Available",
        "income": income,
        "rent-max": rent
    }
    
    # Make GET request and parse JSON
# Make GET request and parse JSON
    response = requests.get(base_url, params=query_params)
    try:
        response.raise_for_status()
        apartments = response.json()
    except requests.exceptions.HTTPError as err:
        print("Error fetching data:", err)
        raise SystemExit(err)
    
    # Output apartments data to a JSON file
    if apartments:
        data = {
            "Client": client_name,
            "Apartments": apartments
        }
        file_name = f"{client_name}_apartments.json"
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        # Convert JSON to text file
        with open(f"{client_name}_apartments.txt", 'w') as txt_file:
            txt_file.write(json.dumps(data, indent=4))
