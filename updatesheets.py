import gspread
from google.oauth2.service_account import Credentials
import csv

# ---------------- Google Sheets setup ----------------
SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = 'credentials.json'  # Path to your service account credentials
SHEET_ID = '' # Replace with your actual Google Sheet ID

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ---------------- Load CSV data ----------------
csv_file_path = 'sku_results.csv'  # Replace with your CSV file path
csv_data = {}

with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    next(reader)  # Skip CSV header row if exists
    for row in reader:
        if len(row) >= 2:
            csv_key = row[0].strip()
            csv_value = row[1].strip()
            csv_data[csv_key] = csv_value

print(f'Loaded {len(csv_data)} rows from CSV.')

# ---------------- Load Google Sheet data ----------------
sheet_data = sheet.get_all_values()

# Track updates to batch-send later
updates = []

# Iterate through sheet data and match/update values
for idx, row in enumerate(sheet_data, start=1):  # Google Sheets indexing starts from 1
    sheet_key = row[0].strip()
    if sheet_key in csv_data:
        csv_value = csv_data[sheet_key]
        updates.append({
            'range': f'C{idx}',
            'values': [[csv_value]]
        })

# Perform batch update
if updates:
    sheet.batch_update(updates)
    print(f'Updated {len(updates)} rows in Google Sheet.')
else:
    print('No matching rows found; no updates made.')
