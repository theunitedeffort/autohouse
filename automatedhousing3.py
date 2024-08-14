#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import re

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import pandas as pd
import requests
import yaml

load_dotenv()

# Google Drive API setup
scope = ['https://www.googleapis.com/auth/drive']
service_account_json_key = os.environ['SERVICE_ACCOUNT_CREDENTIAL_FILE']
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key,
    scopes=scope
)
service = build('drive', 'v3', credentials=credentials)

csv_bytes = service.files().export_media(fileId="1eRDtHWCFHYPDJQv_QCeqGUmPQJsdv-aQAnGfK8LnMfU", mimeType='text/csv').execute()
# The loaded CSV should always be relatively small (~100 lines) so we can just
# load it into pandas directly from memory.
df = pd.read_csv(io.BytesIO(csv_bytes))

# Base URL for the housing data
base_url = "https://www.theunitedeffort.org/data/housing/affordable-housing/filter"

# Function to create URLs based on client data
def generate_urls(df):
  urls = []
  for _, row in df.iterrows():
    print(f'Processing row: {row.to_dict()}')
    if 'Affordable Housing' not in row['Housing Options']:
      print('Affordable housing not specified as a housing option. Skipping.')
      continue
    client_id = row['Record ID']
    params = {}

    params['availability'] = ['Available', 'Waitlist Open']

    params['city'] = row['Location Preferences'].split('|')

    print(f'Raw rent string: {row['Monthly Rent Budget']}')
    # Blow away dates in case the year is interpreted as a rent value
    rent_max = re.sub(r'(\d{4}|\d{1,2})[/\-]\d{1,2}[/\-](\d{4}|\d{1,2})',
      '[date]', row['Monthly Rent Budget'])
    # Numbers may be written as e.g. "1K" so replace that with "1,000"
    rent_max = re.sub(r'(\d)K', r'\1,000', rent_max)
    # Get 3 or 4 digit numbers and strip out any comma separators
    rent_matches = [int(m.replace(',', '')) for m in re.findall(r'\d?,?\d{3,4}', rent_max)]
    if rent_matches:
      params['rentMax'] = max(rent_matches)
      print(f'parsed max rent: {params['rentMax']}')
    else:
      print('no max rent found')
    params['includeUnknownRent'] = 'on'

    # TODO: Perhaps include veterans and disabled here by default until
    # we collect that information in our search preferences.
    params['populationsServed'] = ['General Population']
    if row['Age']:
      age = None
      try:
       age = int(row['Age'])
      except ValueError:
        pass
      if age and age > 55:
        params['populationsServed'].append('Seniors')

    print(f'final query parameters: {params}\n')
    req = requests.PreparedRequest()
    req.prepare_url(base_url, params)
    urls.append({'client_id': client_id, 'url': req.url})
  return urls

# Generate URLs and save to a YAML file
urls = generate_urls(df)

with open('urls.yaml', 'w') as file:
  yaml.dump(urls, file, default_flow_style=False)

# You can now run urlwatch with the generated urls.yaml file
# os.system('urlwatch --urls urls.yaml --config config.yaml')
