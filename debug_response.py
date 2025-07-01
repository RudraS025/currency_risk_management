#!/usr/bin/env python3
"""
Debug Response Format
Check what the API is actually returning
"""

import requests
import json
from datetime import datetime

# Live Heroku URL
BASE_URL = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"

def debug_response():
    """Debug the actual response format"""
    print("🔍 DEBUG: Checking API Response Format")
    print("=" * 50)
    
    test_data = {
        "lc_id": "DEMO-LC-001",
        "lc_amount": 500000,
        "lc_currency": "USD",  
        "contract_rate": 82.50,
        "issue_date": "2025-04-02",
        "maturity_date": "2025-06-01",
        "business_type": "import"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/calculate-backdated-pl",
            json=test_data,
            timeout=120
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Response Size: {len(response.text)} bytes")
        
        if response.status_code == 200:
            # Print raw response
            print(f"\nRaw Response (first 500 chars):")
            print(response.text[:500])
            
            # Parse JSON
            data = response.json()
            print(f"\nParsed JSON structure:")
            print(f"Keys: {list(data.keys())}")
            
            # Check if data is nested
            if 'data' in data:
                print(f"Data keys: {list(data['data'].keys())}")
                inner_data = data['data']
                
                # Check pl_summary structure
                if 'pl_summary' in inner_data:
                    pl_summary = inner_data['pl_summary']
                    print(f"\nPL Summary keys: {list(pl_summary.keys())}")
                    print(f"PL Summary values:")
                    for key, value in pl_summary.items():
                        print(f"  {key}: {value}")
                
                # Check risk_metrics structure
                if 'risk_metrics' in inner_data:
                    risk_metrics = inner_data['risk_metrics']
                    print(f"\nRisk Metrics keys: {list(risk_metrics.keys())}")
                    print(f"Risk Metrics values:")
                    for key, value in risk_metrics.items():
                        print(f"  {key}: {value}")
                        
                # Check lc_details
                if 'lc_details' in inner_data:
                    lc_details = inner_data['lc_details']
                    print(f"\nLC Details keys: {list(lc_details.keys())}")
                    print(f"LC Details values:")
                    for key, value in lc_details.items():
                        print(f"  {key}: {value}")
                        
                # Check daily_pl
                if 'daily_pl' in inner_data:
                    daily_pl = inner_data['daily_pl']
                    print(f"\nDaily P&L: {len(daily_pl)} records")
                    print(f"First record: {daily_pl[0] if daily_pl else 'None'}")
                    print(f"Last record: {daily_pl[-1] if daily_pl else 'None'}")
                    
            else:
                print(f"\nDirect Values:")
                print(f"  final_pl: {data.get('final_pl')}")
                print(f"  max_profit: {data.get('max_profit')}")
                print(f"  max_loss: {data.get('max_loss')}")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_response()
