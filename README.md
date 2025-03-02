# Crypto Data Updater

This project fetches cryptocurrency market data from the CoinGecko API, analyzes it, and updates a Google Sheets document with real-time insights. The script runs automatically using GitHub Actions every 5 minutes or can be triggered manually.

Google Sheet link- https://docs.google.com/spreadsheets/d/1qHxDgo1PyT59hHwRJmtml1xdMS5scz86j34Zlu4IoWY/edit?gid=0#gid=0

## Features
- Fetches real-time cryptocurrency data from the CoinGecko API.
- Analyzes top 5 cryptocurrencies by market cap.
- Computes key insights such as average price, highest/lowest 24h price change.
- Updates Google Sheets with:
  - Full cryptocurrency market data.
  - Top 5 cryptocurrencies by market cap.
  - Summary of market analysis.
- Automated execution via GitHub Actions.

## Requirements
### **1. Google Cloud Setup**
- Create a Google Cloud Service Account.
- Enable Google Sheets & Google Drive APIs.
- Generate and download a JSON key file.
- Convert the JSON file to a Base64 string and store it as a GitHub Secret named `GCP_SERVICE_ACCOUNT`.

### **2. Required Python Libraries**
Install dependencies using:
```sh
pip install -r requirements.txt
```

### **3. Google Sheets Setup**
- Create a Google Sheet and get its **Sheet ID** (found in the URL).
- Share it with your Google Cloud service account email.

## Environment Variables
| Variable | Description |
|----------|-------------|
| `GCP_SERVICE_ACCOUNT` | Base64-encoded Google Cloud service account JSON |

## Usage
Run the script locally:
```sh
python script.py
```

## GitHub Actions Workflow
The workflow automates script execution every **5 minutes** and supports manual runs.

### **Workflow Configuration (`.github/workflows/crypto_update.yml`)**
```yaml
name: Crypto Data Updater

on:
  schedule:
    - cron: '*/5 * * * *'  # Runs every 5 minutes
  workflow_dispatch:  # Manual execution

jobs:
  update_crypto_data:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set Up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install Dependencies
      run: |
        pip install -r requirements.txt

    - name: Verify Repository Files
      run: ls -R

    - name: Check Environment Variables
      run: echo "GCP_SERVICE_ACCOUNT is set"
      env:
        GCP_SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT }}

    - name: Run Crypto Data Script
      run: python -u script.py || { echo "❌ ERROR: script.py failed"; exit 1; }
      env:
        GCP_SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

## Expected Output
The script updates three sheets in your Google Spreadsheet:
1. **Main Data Sheet** - Full cryptocurrency market data.
2. **Top 5 Cryptos** - Top 5 coins by market cap.
3. **Analysis Summary** - Key insights like average price, biggest gainers/losers.

## Troubleshooting
- Ensure the Google Sheets API is enabled in Google Cloud.
- Verify that the service account has edit permissions on the Google Sheet.
- Check GitHub Actions logs for API errors.
- Manually run `python script.py` to debug locally.

## License
This project is open-source under the MIT License.

---
🚀 **Happy coding!**

