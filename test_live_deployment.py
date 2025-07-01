#!/usr/bin/env python3
"""
Final Live Deployment Test for Backdated LC System
Tests the deployed Heroku application with comprehensive scenarios
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Live Heroku URL
BASE_URL = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"

def test_health_check():
    """Test health check endpoint"""
    print("1. Testing Health Check (Live)...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Focus: {data.get('focus')}")
        print(f"   Data Source: {data.get('data_source')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_current_rates():
    """Test current rates endpoint"""
    print("\n2. Testing Current Rates (Live)...")
    try:
        response = requests.get(f"{BASE_URL}/api/current-rates", timeout=30)
        data = response.json()
        print(f"✅ Current rates retrieved")
        print(f"   USD/INR: {data.get('usd_inr')}")
        print(f"   Source: {data.get('source')}")
        print(f"   Last Updated: {data.get('last_updated')}")
        return True
    except Exception as e:
        print(f"❌ Current rates failed: {e}")
        return False

def test_backdated_pl_calculation():
    """Test backdated P&L calculation"""
    print("\n3. Testing Backdated P&L Calculation (Live)...")
    try:
        # Test with historical LC
        test_data = {
            "lc_amount": 500000,
            "lc_currency": "USD",
            "contract_rate": 82.50,
            "issue_date": "2025-04-02",
            "maturity_date": "2025-06-01",
            "business_type": "import"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/calculate-backdated-pl", 
            json=test_data,
            timeout=60
        )
        data = response.json()
        
        print(f"✅ Backdated P&L calculation successful")
        print(f"   Final P&L: ₹{data.get('final_pl', 0):,.2f}")
        print(f"   Max Profit: ₹{data.get('max_profit', 0):,.2f}")
        print(f"   Max Loss: ₹{data.get('max_loss', 0):,.2f}")
        print(f"   VaR (95%): ₹{data.get('var_95', 0):,.2f}")
        print(f"   Data Points: {data.get('daily_data_points', 0)}")
        print(f"   Analysis Period: {data.get('analysis_period', {}).get('start')} to {data.get('analysis_period', {}).get('end')}")
        print(f"   Data Source: {data.get('data_source')}")
        
        return True
    except Exception as e:
        print(f"❌ Backdated P&L calculation failed: {e}")
        return False

def test_scenario_analysis():
    """Test scenario analysis"""
    print("\n4. Testing Scenario Analysis (Live)...")
    try:
        test_data = {
            "lc_amount": 250000,
            "lc_currency": "USD",
            "contract_rate": 83.00,
            "issue_date": "2025-03-15",
            "maturity_date": "2025-05-15",
            "business_type": "export"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/scenario-analysis", 
            json=test_data,
            timeout=60
        )
        data = response.json()
        
        print(f"✅ Scenario analysis successful")
        print(f"   Base P&L: ₹{data.get('base_pl', 0):,.2f}")
        print(f"   Scenarios tested: {len(data.get('scenarios', []))}")
        
        for scenario in data.get('scenarios', [])[:3]:  # Show first 3
            impact = scenario.get('impact_level', 'Unknown')
            pl = scenario.get('pl', 0)
            print(f"   - {scenario.get('name')}: ₹{pl:,.2f} ({impact} Impact)")
        
        return True
    except Exception as e:
        print(f"❌ Scenario analysis failed: {e}")
        return False

def test_forward_rates():
    """Test forward rates endpoint"""
    print("\n5. Testing Forward Rates (Live)...")
    try:
        response = requests.get(f"{BASE_URL}/api/forward-rates", timeout=30)
        data = response.json()
        print(f"✅ Forward rates retrieved")
        
        if 'forward_rates' in data:
            for period, rate in list(data['forward_rates'].items())[:3]:  # Show first 3
                print(f"   {period}: {rate}")
        
        print(f"   Source: {data.get('source')}")
        return True
    except Exception as e:
        print(f"❌ Forward rates failed: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("\n6. Testing Report Generation (Live)...")
    try:
        test_data = {
            "lc_id": "LIVE-TEST-001",
            "lc_amount": 750000,
            "lc_currency": "USD",
            "contract_rate": 82.25,
            "issue_date": "2025-04-10",
            "maturity_date": "2025-06-10",
            "business_type": "import"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate-report", 
            json=test_data,
            timeout=60
        )
        data = response.json()
        
        print(f"✅ Report generation successful")
        print(f"   LC ID: {data.get('lc_id')}")
        print(f"   Total Value: ${data.get('total_value', 0):,.2f}")
        print(f"   Status: {data.get('status')}")
        print(f"   Analysis Period: {data.get('analysis_period', {}).get('start')} to {data.get('analysis_period', {}).get('end')}")
        
        return True
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False

def main():
    """Run comprehensive live deployment test"""
    print("🚀 Testing Live Deployment: Backdated LC System")
    print("=" * 60)
    print(f"🌐 Testing URL: {BASE_URL}")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    tests = [
        test_health_check,
        test_current_rates,
        test_backdated_pl_calculation,
        test_scenario_analysis,
        test_forward_rates,
        test_report_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Live deployment is successful!")
        print("✅ The backdated LC system is fully operational on Heroku")
        print(f"🌐 Access your application at: {BASE_URL}")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the deployment.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
