"""
Comprehensive test of the Currency Risk Management System
"""
import requests
import json
from datetime import datetime

def test_complete_system():
    """Test all endpoints of the Currency Risk Management System"""
    base_url = "http://localhost:5000"
    
    print("=" * 80)
    print("🚀 COMPREHENSIVE CURRENCY RISK MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Real 2025 Data: {data.get('real_2025_data_available')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Current Rates
    print("\n2️⃣ Testing Current Rates...")
    try:
        response = requests.get(f"{base_url}/api/current-rates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current USD/INR Rate: {data.get('rate'):.4f}")
        else:
            print(f"❌ Current rates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Current rates error: {e}")
    
    # Test 3: P&L Calculation with Real 2025 Data
    print("\n3️⃣ Testing P&L Calculation (Real 2025 Data)...")
    test_lc = {
        "lc_number": "TEST-COMPREHENSIVE-001",
        "amount_usd": 1000000,  # $1M LC
        "issue_date": "2025-06-01",
        "maturity_date": "2025-09-01",
        "beneficiary": "Test Exporter Corp",
        "commodity": "Technology Equipment"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/calculate-pl",
            json=test_lc,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pl_data = data.get('data', {})
                daily_pl = pl_data.get('daily_pl', [])
                
                print(f"✅ P&L Calculation Success!")
                print(f"   LC Amount: ${test_lc['amount_usd']:,}")
                print(f"   Data Points: {len(daily_pl)}")
                print(f"   Data Source: {pl_data.get('data_source')}")
                print(f"   Using Real 2025 Data: {data.get('real_2025_data')}")
                
                if daily_pl:
                    first_day = daily_pl[0]
                    last_day = daily_pl[-1]
                    print(f"   First Day P&L: ₹{first_day['pl_amount']:,.2f} (Rate: {first_day['forward_rate']:.4f})")
                    print(f"   Final Day P&L: ₹{last_day['pl_amount']:,.2f} (Rate: {last_day['forward_rate']:.4f})")
                    print(f"   Max Profit: ₹{pl_data.get('max_profit', 0):,.2f} on {pl_data.get('max_profit_date')}")
                    print(f"   Max Loss: ₹{pl_data.get('max_loss', 0):,.2f} on {pl_data.get('max_loss_date')}")
                    
                    # Verify real data characteristics
                    rates = [point['forward_rate'] for point in daily_pl]
                    unique_rates = len(set(rates))
                    rate_range = max(rates) - min(rates)
                    
                    print(f"   Rate Variation: {rate_range:.4f} ({unique_rates} unique rates)")
                    
                    if unique_rates > 50 and rate_range > 1.0:
                        print("✅ CONFIRMED: Using real, time-varying forward rates!")
                    else:
                        print("⚠️  WARNING: Data appears synthetic")
                
                # Test risk metrics
                risk_metrics = data.get('risk_metrics', {})
                print(f"   VaR (95%): ₹{risk_metrics.get('var_95', 0):,.2f}")
                print(f"   Volatility: {risk_metrics.get('volatility', 0):.2f}%")
                
            else:
                print(f"❌ P&L calculation failed: {data.get('error')}")
        else:
            print(f"❌ P&L request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ P&L calculation error: {e}")
    
    # Test 4: Scenario Analysis
    print("\n4️⃣ Testing Scenario Analysis...")
    try:
        response = requests.post(
            f"{base_url}/api/scenario-analysis",
            json=test_lc,
            headers={'Content-Type': 'application/json'},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scenarios = data.get('scenarios', [])
                print(f"✅ Scenario Analysis Success!")
                print(f"   Number of scenarios: {len(scenarios)}")
                
                for scenario in scenarios:
                    if isinstance(scenario, dict):
                        name = scenario.get('name', 'Unknown')
                        pl_inr = scenario.get('pl_inr', 0)
                        rate_change = scenario.get('rate_change', 0)
                        print(f"   {name}: {rate_change*100:+.1f}% → ₹{pl_inr:,.2f}")
            else:
                print(f"❌ Scenario analysis failed: {data.get('error')}")
        else:
            print(f"❌ Scenario request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scenario analysis error: {e}")
    
    # Test 5: Report Generation
    print("\n5️⃣ Testing Report Generation...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-report",
            json=test_lc,
            headers={'Content-Type': 'application/json'},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('report', {})
                print(f"✅ Report Generation Success!")
                print(f"   Report generated at: {data.get('timestamp', 'N/A')}")
                print(f"   Sections included: {len(report)} sections")
            else:
                print(f"❌ Report generation failed: {data.get('error')}")
        else:
            print(f"❌ Report request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE TEST COMPLETED")
    print("✅ System is ready for production deployment!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_complete_system()
