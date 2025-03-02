import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1qHxDgo1PyT59hHwRJmtml1xdMS5scz86j34Zlu4IoWY"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
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


def update_excel(df, top_5, avg_price, highest_change, lowest_change, filename="crypto_data.xlsx"):
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Top 50 Cryptos", index=False)
        top_5.to_excel(writer, sheet_name="Top 5 by Market Cap", index=False)

        
        summary_data = {
            "Metric": ["Average Price (USD)", "Highest 24h Change", "Lowest 24h Change"],
            "Value": [avg_price, f"{highest_change['name']} ({highest_change['price_change_percentage_24h']}%)",
                      f"{lowest_change['name']} ({lowest_change['price_change_percentage_24h']}%)"]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Analysis Summary", index=False)

    print(f"Excel file '{filename}' updated successfully!")

def update_google_sheets():
    print("Fetching live crypto data...")
    data = fetch_crypto_data()
    headers = ["Name", "Symbol", "Price (USD)", "Market Cap", "24h Volume", "24h Change (%)"]
    
    sheet.clear()  # Clear old data
    sheet.append_row(headers)  # Add headers
    sheet.append_rows(data)  # Add new data
    
    print("Google Sheet updated!")

if __name__ == "__main__":
    update_google_sheets()
    
