#!/usr/bin/env python3

import requests
import json

def test_api_directly():
    print("🌐 TESTING API DIRECTLY")
    print("=" * 30)
    
    # Test data
    test_data = {
        "lc_number": "API-TEST-001",
        "amount_usd": 150000,
        "issue_date": "2025-06-01",
        "maturity_date": "2025-08-30",
        "commodity": "Rice",
        "beneficiary": "Test Customer",
        "use_forward_rates": True
    }
    
    print(f"Sending data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        response = requests.post(
            'http://localhost:5000/api/calculate-pl',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("Response Data:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                pl_result = result.get('pl_result', {})
                print(f"\n📊 P&L Results:")
                print(f"  Total P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"  Current Rate: ₹{pl_result.get('spot_rate', 0):.4f}")
                print(f"  Original Rate: ₹{pl_result.get('original_rate', 0):.4f}")
                print(f"  Chart Data: {len(pl_result.get('chart_data', []))} points")
            else:
                print(f"❌ API Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_directly()
