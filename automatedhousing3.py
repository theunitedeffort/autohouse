#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 21:54:55 2024

@author: isaacwang
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from googleapiclient.errors import HttpError
import pandas as pd
import yaml

# Google Drive API setup
scope = ['https://www.googleapis.com/auth/drive']
service_account_json_key = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key,
    scopes=scope
)
service = build('drive', 'v3', credentials=credentials)

# Call the Drive v3 API
results = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)", q='name contains "de"').execute()
items = results.get('files', [])
data = []

for row in items:
    if row["mimeType"] != "application/vnd.google-apps.folder":
        row_data = []
        try:
            row_data.append(round(int(row["size"])/1000000, 2))
        except KeyError:
            row_data.append(0.00)
        row_data.append(row["id"])
        row_data.append(row["name"])
        row_data.append(row["modifiedTime"])
        row_data.append(row["mimeType"])
        data.append(row_data)

cleared_df = pd.DataFrame(data, columns=['size_in_MB', 'id', 'name', 'last_modification', 'type_of_file'])

# File export and download
new_permission = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'ijw91021@gmail.com',
}
try:
    print("a")
    service.permissions().create(fileId='1WrQ1eRIoUWmIPQEacyl_s-P7pbtuRbicFufVNnsLmCY', body=new_permission, transferOwnership=False).execute()
    print("b")
except (AttributeError, HttpError) as error:
    print(f'An error occurred: {error}')

print("c")
request_file = service.files().export_media(fileId="1WrQ1eRIoUWmIPQEacyl_s-P7pbtuRbicFufVNnsLmCY", mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
file = io.BytesIO()
downloader = MediaIoBaseDownload(file, request_file)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print(f'Download {int(status.progress() * 100)}%.')

print("d")
file.seek(0)  # Reset the file pointer to the beginning
with open(f"downloaded_file.xlsx", 'wb') as df:
    df.write(file.read())
print("e")

# Load the downloaded file into a DataFrame
df = pd.read_excel("downloaded_file.xlsx")

# Base URL for the housing data
base_url = "https://www.theunitedeffort.org/housing/affordable-housing/filter?"

# Function to create URLs based on client data
def generate_urls(df):
    urls = []
    for _, row in df.iterrows():
        client_name = row['Client ID']

        # Use default values if certain fields are missing
        preferred_locations = row['Location Preferences'] if pd.notnull(row['Location Preferences']) else "Unknown"
        type_of_units = row['Housing Options'] if pd.notnull(row['Housing Options']) else "Unknown"
        rent = row['Monthly Rent Budget'] if pd.notnull(row['Monthly Rent Budget']) else "Unknown"
        age = row['Age'] if pd.notnull(row['Age']) else "Unknown"

        # Combine multiple locations
        if preferred_locations != "Unknown":
            locations = preferred_locations.split(",")  # Assuming the locations are comma-separated
            location_query = "&".join([f"city={location.strip().replace(' ', '+')}" for location in locations])
        else:
            location_query = "city=Unknown"

        # Construct the URL with additional default values for other parameters
        query_params = [
            location_query,
            f"unitType={type_of_units}",
            "availability=Available",
            "populationsServed=Unknown",  # You can change this as needed
            f"rentMax={rent}",
            "includeUnknownRent=on",
            "income=Unknown",  # You can change this as needed
            "includeUnknownIncome=on",
            "propertyName="
        ]
        query_str = "&".join(query_params)
        url = base_url + query_str
        urls.append({"client_name": client_name, "url": url})

    return urls

# Generate URLs and save to a YAML file
urls = generate_urls(df)

with open('urls.yaml', 'w') as file:
    yaml.dump(urls, file, default_flow_style=False)

# You can now run urlwatch with the generated urls.yaml file
# os.system('urlwatch --urls urls.yaml --config config.yaml')
