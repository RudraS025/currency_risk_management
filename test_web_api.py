"""
Test script to verify the web API returns meaningful P&L results
"""
import requests
import json
from datetime import datetime, timedelta

def test_web_api():
    """Test the web API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    # Test data
    test_data = {
        "lc_number": "WEB-TEST-001",
        "amount_usd": 500000,
        "issue_date": "2024-01-01",
        "maturity_date": "2024-04-01",
        "beneficiary": "Test Exporter",
        "commodity": "Basmati Rice"
    }
    
    print("=" * 60)
    print("TESTING WEB API ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Current Rates
    print("\n1. Testing Current Rates API...")
    try:
        response = requests.get(f"{base_url}/api/current-rates")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Rate: {data.get('rate', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 2: P&L Calculation
    print("\n2. Testing P&L Calculation API...")
    try:
        response = requests.post(f"{base_url}/api/calculate-pl", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                print(f"✅ P&L Calculation Success!")
                print(f"   Current P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"   Current Rate: {pl_result.get('spot_rate', 0):.4f}")
                print(f"   Original Rate: {pl_result.get('original_rate', 0):.4f}")
                print(f"   Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"   Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"   Chart Data Points: {len(pl_result.get('chart_data', []))}")
                
                # Check if we got meaningful results
                if abs(pl_result.get('total_pl_inr', 0)) > 1000:
                    print("✅ MEANINGFUL P&L VALUES RETURNED!")
                else:
                    print("⚠️  P&L values seem low - might be using fallback")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Scenario Analysis
    print("\n3. Testing Scenario Analysis API...")
    try:
        response = requests.post(f"{base_url}/api/scenario-analysis", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scenarios = data.get('scenarios', [])
                print(f"✅ Scenario Analysis Success! ({len(scenarios)} scenarios)")
                for scenario in scenarios:
                    print(f"   {scenario['scenario_name']}: ₹{scenario['pl_inr']:,.2f} ({scenario['impact']})")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 4: Report Generation
    print("\n4. Testing Report Generation API...")
    try:
        response = requests.post(f"{base_url}/api/generate-report", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('report', {})
                print(f"✅ Report Generation Success!")
                
                # Check if report has meaningful data
                pl_analysis = report.get('pl_analysis', {})
                if pl_analysis:
                    print(f"   Current P&L: ₹{pl_analysis.get('current_pl', 0):,.2f}")
                    print(f"   Max Profit: ₹{pl_analysis.get('max_profit', 0):,.2f}")
                    print(f"   Days Analyzed: {pl_analysis.get('total_days_analyzed', 0)}")
                
                exec_summary = report.get('executive_summary', {})
                if exec_summary:
                    print(f"   Report Type: {exec_summary.get('title', 'N/A')}")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "=" * 60)
    print("WEB API TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_web_api()
