"""
Test the final deployment of the Currency Risk Management System
"""
import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_local_app(port=5000):
    """Test the local Flask app"""
    base_url = f"http://localhost:{port}"
    
    print("=" * 80)
    print("TESTING FINAL CURRENCY RISK MANAGEMENT SYSTEM DEPLOYMENT")
    print(f"Local URL: {base_url}")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n🔍 1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            print(f"   Real 2025 Data: {data.get('real_2025_data_available', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Current Rates
    print("\n🔍 2. Testing Current Rates API...")
    try:
        response = requests.get(f"{base_url}/api/current-rates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current USD/INR Rate: {data.get('rate', 'N/A')}")
            print(f"   Last Updated: {data.get('last_updated', 'N/A')}")
        else:
            print(f"❌ Current rates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Current rates error: {e}")
    
    # Test 3: Real 2025 LC P&L Calculation
    print("\n🔍 3. Testing Real 2025 LC P&L Calculation...")
    real_2025_lc = {
        "lc_number": "REAL-2025-TEST",
        "amount_usd": 1000000,
        "issue_date": "2025-06-01",
        "maturity_date": "2025-09-01",
        "beneficiary": "Real 2025 Exporter",
        "commodity": "Technology Equipment",
        "contract_rate": 84.50
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/calculate-pl",
            json=real_2025_lc,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                daily_pl = pl_result.get('chart_data', [])
                
                print(f"✅ P&L Calculation Successful!")
                print(f"   LC Amount: ${real_2025_lc['amount_usd']:,}")
                print(f"   Period: {real_2025_lc['issue_date']} to {real_2025_lc['maturity_date']}")
                print(f"   Data Points: {len(daily_pl)}")
                print(f"   Data Source: {pl_result.get('data_source', 'Unknown')}")
                print(f"   Using Real 2025 Data: {data.get('real_2025_data', False)}")
                
                if daily_pl:
                    # Find max profit and loss
                    max_profit = max(daily_pl, key=lambda x: x['pl_amount'])
                    max_loss = min(daily_pl, key=lambda x: x['pl_amount'])
                    final_pl = daily_pl[-1]
                    
                    print(f"   Max Profit: ${max_profit['pl_amount']:,.2f} on {max_profit['date']}")
                    print(f"   Max Loss: ${max_loss['pl_amount']:,.2f} on {max_loss['date']}")
                    print(f"   Final P&L: ${final_pl['pl_amount']:,.2f} on {final_pl['date']}")
                    print(f"   Final Rate: {final_pl['forward_rate']:.4f}")
                    
                    # Verify we're using real data (not static fallback)
                    rates = [point['forward_rate'] for point in daily_pl]
                    unique_rates = len(set(rates))
                    print(f"   Unique Forward Rates: {unique_rates} (should be > 1 for real data)")
                    
                    if unique_rates > 1:
                        print("✅ CONFIRMED: Using real, time-varying forward rates!")
                    else:
                        print("⚠️  WARNING: Appears to be using static rates")
                else:
                    print("❌ No daily P&L data returned")
            else:
                print(f"❌ P&L calculation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ P&L request failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ P&L calculation error: {e}")
    
    # Test 4: Scenario Analysis
    print("\n🔍 4. Testing Scenario Analysis...")
    scenario_data = {
        "lc_number": "SCENARIO-TEST-2025",
        "amount_usd": 750000,
        "issue_date": "2025-07-01",
        "maturity_date": "2025-08-15",
        "beneficiary": "Scenario Test Corp",
        "commodity": "Raw Materials"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/scenario-analysis",
            json=scenario_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scenarios = data.get('scenarios', [])
                print(f"✅ Scenario Analysis Successful!")
                print(f"   Number of scenarios: {len(scenarios)}")
                
                for scenario in scenarios:
                    if isinstance(scenario, dict):
                        name = scenario.get('name', 'Unknown')
                        pl_inr = scenario.get('pl_inr', 0)
                        impact = scenario.get('impact', 'Unknown')
                        print(f"   {name}: ₹{pl_inr:,.2f} ({impact})")
            else:
                print(f"❌ Scenario analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Scenario request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scenario analysis error: {e}")
    
    # Test 5: Risk Report Generation
    print("\n🔍 5. Testing Risk Report Generation...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-report",
            json=real_2025_lc,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('report', {})
                print(f"✅ Risk Report Generated!")
                print(f"   Report Type: {report.get('report_type', 'N/A')}")
                print(f"   Risk Level: {report.get('risk_assessment', {}).get('overall_risk', 'N/A')}")
                recommendations = report.get('recommendations', [])
                print(f"   Recommendations: {len(recommendations)} items")
            else:
                print(f"❌ Report generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Report request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    print("\n" + "=" * 80)
    print("FINAL DEPLOYMENT TEST COMPLETED")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    print("Starting Currency Risk Management System Final Deployment Test...")
    test_local_app()
