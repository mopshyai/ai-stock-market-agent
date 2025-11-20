#!/usr/bin/env python3
"""
ZERODHA LOGIN HELPER
Generates daily access token for Kite Connect API
"""

import os
from kiteconnect import KiteConnect
import webbrowser
import sys

# API Credentials
API_KEY = os.getenv('KITE_API_KEY', 'za11xi3a1sa08nxl')
API_SECRET = os.getenv('KITE_API_SECRET')

if not API_SECRET:
    print("❌ Error: KITE_API_SECRET not found.")
    print("Please enter your API Secret from the Zerodha Developer Dashboard:")
    API_SECRET = input("API Secret: ").strip()

kite = KiteConnect(api_key=API_KEY)

def generate_token():
    print(f"1. Opening login page for API Key: {API_KEY}")
    login_url = kite.login_url()
    webbrowser.open(login_url)
    
    print("\n2. Login to Zerodha in the browser.")
    print("3. After login, you will be redirected to: http://localhost:8501/?request_token=...")
    print("4. Copy the 'request_token' value from the URL bar.")
    
    request_token = input("\nPaste Request Token here: ").strip()
    
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        
        print("\n✅ Access Token Generated Successfully!")
        print(f"Access Token: {access_token}")
        
        # Save to environment file or print export command
        print("\nRun this command to set the token for the current session:")
        print(f"export KITE_ACCESS_TOKEN='{access_token}'")
        
        # Optional: Save to a temporary file for the app to read
        with open(".kite_token", "w") as f:
            f.write(access_token)
        print("\nToken saved to .kite_token file for local app usage.")
        
    except Exception as e:
        print(f"\n❌ Error generating session: {e}")

if __name__ == "__main__":
    print("🚀 Zerodha Kite Login Helper")
    generate_token()
