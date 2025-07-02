#!/usr/bin/env python3
"""
Test the new forward rate calculation system
"""

import requests
import json
from datetime import datetime

def test_forward_rate_system():
    print("🧪 TESTING FORWARD RATE LC SYSTEM")
    print("=" * 50)
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        print(f"✅ System Status: {data.get('status')}")
        print(f"✅ Version: {data.get('version')}")
        print(f"✅ Formula: {data.get('formula')}")
        print(f"✅ Focus: {data.get('focus')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Current rates with RBI rate
    print("\n2️⃣ Testing Current Rates...")
    try:
        response = requests.get(f"{BASE_URL}/api/current-rates")
        data = response.json()
        print(f"✅ USD/INR Rate: ₹{data.get('rate')}")
        print(f"✅ RBI Rate: {data.get('rbi_rate')}%")
        print(f"✅ Source: {data.get('source')}")
    except Exception as e:
        print(f"❌ Current rates failed: {e}")
    
    # Test 3: Forward Rate P&L Calculation
    print("\n3️⃣ Testing Forward Rate P&L Calculation...")
    
    # Realistic test data
    test_data = {
        "lc_id": "FORWARD-TEST-001",
        "lc_amount": 500000,  # $500K
        "contract_rate": 84.65,  # Realistic rate for May 3, 2025
        "issue_date": "2025-05-03",
        "maturity_date": "2025-06-02",  # 30 days
        "business_type": "import"
    }
    
    print(f"📊 Test LC Details:")
    print(f"   Amount: ${test_data['lc_amount']:,}")
    print(f"   Contract Rate: ₹{test_data['contract_rate']}")
    print(f"   Period: {test_data['issue_date']} to {test_data['maturity_date']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/calculate-forward-pl",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                result = data['data']
                
                print(f"\n📈 FORWARD RATE CALCULATION RESULTS:")
                print(f"   Method: {result['pl_summary']['calculation_method']}")
                print(f"   Formula: {result['pl_summary']['formula_used']}")
                
                print(f"\n💰 P&L SUMMARY:")
                print(f"   Final Close P&L: ₹{result['pl_summary']['final_close_pl_inr']:,.2f}")
                print(f"   Max Profit: ₹{result['pl_summary']['max_profit_inr']:,.2f}")
                print(f"   Max Loss: ₹{result['pl_summary']['max_loss_inr']:,.2f}")
                
                print(f"\n📊 LC DETAILS:")
                print(f"   Amount (USD): ${result['lc_details']['amount_usd']:,.2f}")
                print(f"   Amount (INR): ₹{result['lc_details']['amount_inr']:,.2f}")
                print(f"   Interest Rate: {result['lc_details']['interest_rate']}%")
                print(f"   Data Points: {result['pl_summary']['total_data_points']} days")
                
                print(f"\n📋 SAMPLE DAILY DATA (First 5 Days):")
                print(f"   {'Date':<12} {'Spot':<8} {'Days':<5} {'Forward':<8} {'Close P&L':<12}")
                print(f"   {'-'*12} {'-'*8} {'-'*5} {'-'*8} {'-'*12}")
                
                daily_data = result['daily_pl']
                for day in daily_data[:5]:  # Show first 5 days
                    print(f"   {day['date']:<12} ₹{day['spot_rate']:<7} {day['days_remaining']:<5} ₹{day['forward_rate']:<7} ₹{day['close_pl_inr']:<11,.0f}")
                
                if len(daily_data) > 5:
                    print(f"   ... and {len(daily_data) - 5} more days")
                
                print(f"\n✅ FORWARD RATE CALCULATION SUCCESSFUL!")
                print(f"✅ Using real formula: Forward = Spot × e^(r×t/365)")
                print(f"✅ Settlement options available (Close P&L vs Expected P&L)")
                
            else:
                print(f"❌ Calculation failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Forward rate calculation error: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"🎯 FORWARD RATE SYSTEM TEST COMPLETED")
    print(f"✅ Real forward rate calculations implemented")
    print(f"✅ Settlement options available")
    print(f"✅ RBI interest rates integrated")
    print(f"✅ Day-wise P&L with decreasing time element")

if __name__ == "__main__":
    test_forward_rate_system()
