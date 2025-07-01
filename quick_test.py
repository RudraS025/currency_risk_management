#!/usr/bin/env python3
"""
Quick Website Test - Exactly what the user sees
"""

import requests
import json

BASE_URL = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"

def quick_test():
    print("🌐 QUICK WEBSITE TEST")
    print("=" * 40)
    
    # Test exactly what the website form sends
    print("📊 Testing with website form data...")
    form_data = {
        "lc_id": "DEMO-LC-001",
        "lc_amount": 500000,
        "lc_currency": "USD", 
        "contract_rate": 82.50,
        "issue_date": "2025-04-02",  # 2 months ago
        "maturity_date": "2025-06-01",  # 1 month ago 
        "business_type": "import"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/calculate-backdated-pl",
            json=form_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                pl_summary = data['data']['pl_summary']
                print("✅ SUCCESS - Real P&L Results:")
                print(f"   Final P&L: ₹{pl_summary['final_pl_inr']:,.2f}")
                print(f"   Max Profit: ₹{pl_summary['max_profit_inr']:,.2f}")
                print(f"   Max Loss: ₹{pl_summary['max_loss_inr']:,.2f}")
                print(f"   Data Points: {pl_summary['total_data_points']} days")
                print(f"   Data Source: {pl_summary['data_source']}")
                print("\n🎉 The website WILL show real results!")
            else:
                print("❌ No data in response")
                print(f"Response: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 40)

if __name__ == "__main__":
    quick_test()
