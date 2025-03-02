import requests
import base64
import pandas as pd
import gspread
import json
import os
from google.oauth2.service_account import Credentials

SHEET_ID = "1qHxDgo1PyT59hHwRJmtml1xdMS5scz86j34Zlu4IoWY"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Decode base64 secret from GitHub Secrets
service_account_json = os.getenv("GCP_SERVICE_ACCOUNT")

if not service_account_json:
    print("❌ ERROR: GCP_SERVICE_ACCOUNT environment variable is missing!")
    exit(1)

# Decode base64 secret
service_account_json = base64.b64decode(service_account_json).decode("utf-8")

# Load credentials
service_account_info = json.loads(service_account_json)
CREDS = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# Authorize gspread client
client = gspread.authorize(CREDS)
sheet = client.open_by_key(SHEET_ID).worksheet("crypto_data")

def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else: 
        print(f"❌ ERROR: Failed to fetch data. Status Code: {response.status_code}")
        print("Response:", response.text)
        exit(1)

def analyze_data(data):
    df = pd.DataFrame(data)[["name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]]
   
    top_5 = df.nlargest(5, "market_cap")
    avg_price = df["current_price"].mean()
    highest_change = df.loc[df["price_change_percentage_24h"].idxmax()]
    lowest_change = df.loc[df["price_change_percentage_24h"].idxmin()]

    return df, top_5, avg_price, highest_change, lowest_change

def update_google_sheets():

    print("✅ Script started successfully.")
    data = fetch_crypto_data()
    if not data:
        print("❌ No data fetched from API!")
        exit(1)



    df, top_5, avg_price, highest_change, lowest_change = analyze_data(data)
    
    # Convert data to list format for Google Sheets
    rows = df.values.tolist()
    top_5_rows = top_5.values.tolist()

    headers = ["Name", "Symbol", "Price (USD)", "Market Cap", "24h Volume", "24h Change (%)"]

    # **Clear old data & update main crypto data**
    sheet.clear()
    sheet.append_row(headers)
    sheet.append_rows(rows)
    
    # **Create or update Top 5 Cryptos sheet**
    try:
    top_5_sheet = client.open_by_key(SHEET_ID).add_worksheet(title="Top 5 Cryptos", rows=10, cols=6)
    except (gspread.exceptions.APIError, gspread.exceptions.WorksheetNotFound):
    top_5_sheet = client.open_by_key(SHEET_ID).worksheet("Top 5 Cryptos")
    top_5_sheet.clear()

    top_5_sheet.append_row(headers)
    top_5_sheet.append_rows(top_5_rows)

    # **Create or update Summary Data sheet**
    summary_headers = ["Metric", "Value"]
    summary_data = [
        ["Average Price (USD)", avg_price],
        ["Highest 24h Change", f"{highest_change['name']} ({highest_change['price_change_percentage_24h']}%)"],
        ["Lowest 24h Change", f"{lowest_change['name']} ({lowest_change['price_change_percentage_24h']}%)"]
    ]

    try:
        summary_sheet = client.open_by_key(SHEET_ID).add_worksheet(title="Analysis Summary", rows=10, cols=2)
    except gspread.exceptions.APIError:
        summary_sheet = client.open_by_key(SHEET_ID).worksheet("Analysis Summary")
        summary_sheet.clear()

    summary_sheet.append_row(summary_headers)
    summary_sheet.append_rows(summary_data)

    print("Google Sheets updated successfully with analysis!")

if __name__ == "__main__":
    update_google_sheets()
