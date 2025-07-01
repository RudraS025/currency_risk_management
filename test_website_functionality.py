#!/usr/bin/env python3
"""
Simple Manual Test for Live Website
Tests the key functionality that users will actually use
"""

import requests
import json
from datetime import datetime

# Live Heroku URL
BASE_URL = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"

def test_web_form_data():
    """Test the exact same data as the web form would send"""
    print("🧪 Testing Web Form Simulation")
    print("=" * 50)
    
    # Simulate exact form data from the website
    test_data = {
        "lc_id": "DEMO-LC-001",  # This is what the form sends
        "lc_amount": 500000,
        "lc_currency": "USD",
        "contract_rate": 82.50,
        "issue_date": "2025-04-02",
        "maturity_date": "2025-06-01",
        "business_type": "import"
    }
    
    print(f"📊 Sending form data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/calculate-backdated-pl",
            json=test_data,
            timeout=120,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📈 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Backdated P&L calculation completed")
            print(f"   Final P&L: ₹{data.get('final_pl', 0):,.2f}")
            print(f"   Max Profit: ₹{data.get('max_profit', 0):,.2f}")
            print(f"   Max Loss: ₹{data.get('max_loss', 0):,.2f}")
            print(f"   VaR (95%): ₹{data.get('var_95', 0):,.2f}")
            print(f"   Data Points: {data.get('daily_data_points', 0)}")
            print(f"   Data Source: {data.get('data_source')}")
            
            analysis_period = data.get('analysis_period', {})
            if analysis_period:
                print(f"   Period: {analysis_period.get('start')} to {analysis_period.get('end')}")
            
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_current_rates():
    """Test current rates API"""
    print(f"\n💱 Testing Current Rates API")
    try:
        response = requests.get(f"{BASE_URL}/api/current-rates", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current USD/INR Rate: {data.get('usd_inr', 'N/A')}")
            print(f"   Source: {data.get('source', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run focused web tests"""
    print("🌐 LIVE WEBSITE FUNCTIONALITY TEST")
    print("🚀 Testing: https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com")
    print("🕒 Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)
    
    # Test current rates first
    rates_ok = test_current_rates()
    
    # Test the main functionality
    calc_ok = test_web_form_data()
    
    print("\n" + "=" * 70)
    print("🎯 SUMMARY:")
    print(f"   💱 Current Rates API: {'✅ WORKING' if rates_ok else '❌ FAILED'}")
    print(f"   📊 P&L Calculator: {'✅ WORKING' if calc_ok else '❌ FAILED'}")
    
    if rates_ok and calc_ok:
        print("\n🎉 SUCCESS: Website is fully functional!")
        print("👍 Users can now:")
        print("   - View live USD/INR rates")
        print("   - Calculate backdated LC P&L")
        print("   - Get real historical analysis")
    else:
        print("\n⚠️  Some issues detected. Check logs for details.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
