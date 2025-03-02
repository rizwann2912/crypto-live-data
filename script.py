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
service_account_json = base64.b64decode(os.getenv("GCP_SERVICE_ACCOUNT")).decode("utf-8")

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
        "per_page": 50,  # Top 50 cryptocurrencies
        "page": 1,
        "sparkline": False
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else: 
        print("Error fetching data:", response.status_code)
        return None

def analyze_data(data):
    df = pd.DataFrame(data)[["name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]]
   
    top_5 = df.nlargest(5, "market_cap")
    avg_price = df["current_price"].mean()
    highest_change = df.loc[df["price_change_percentage_24h"].idxmax()]
    lowest_change = df.loc[df["price_change_percentage_24h"].idxmin()]

    return df, top_5, avg_price, highest_change, lowest_change

def update_google_sheets():
    print("Fetching live crypto data...")
    data = fetch_crypto_data()
    
    if not data:
        print("No data fetched.")
        return

    df, top_5
