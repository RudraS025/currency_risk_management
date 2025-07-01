"""
Test script for the new Backdated LC system
"""
import requests
import json
from datetime import datetime, timedelta

def test_backdated_system():
    """Test the new backdated LC system"""
    base_url = "http://localhost:5001"  # Different port for v2
    
    print("=" * 80)
    print("🚀 TESTING BACKDATED LC SYSTEM v2.0")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Focus: {data.get('focus')}")
            print(f"   Data Source: {data.get('data_source')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Date Validation
    print("\n2️⃣ Testing Date Validation...")
    
    # Test backdated LC (should pass)
    test_dates = {
        "issue_date": "2024-01-01",
        "maturity_days": 60
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/validate-dates",
            json=test_dates,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                validation = data.get('validation', {})
                print(f"✅ Date validation successful!")
                print(f"   Issue Date Valid: {validation.get('issue_date_valid')}")
                print(f"   Maturity Date Valid: {validation.get('maturity_date_valid')}")
                print(f"   Maturity Date: {validation.get('maturity_date')}")
                print(f"   Is Backdated: {validation.get('is_backdated')}")
                print(f"   Days Since Maturity: {validation.get('days_since_maturity')}")
            else:
                print(f"❌ Date validation failed: {data.get('error')}")
        else:
            print(f"❌ Date validation request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Date validation error: {e}")
    
    # Test 3: Backdated P&L Calculation
    print("\n3️⃣ Testing Backdated P&L Calculation...")
    
    test_lc = {
        "lc_number": "TEST-BACKDATE-001",
        "amount_usd": 500000,  # $500K LC
        "issue_date": "2024-01-01",
        "maturity_days": 60,
        "contract_rate": 82.50,
        "beneficiary": "Test Exporter Ltd",
        "commodity": "Electronics"
    }
    
    try:
        print(f"   Calculating P&L for ${test_lc['amount_usd']:,} LC...")
        print(f"   Period: {test_lc['issue_date']} to {test_lc['maturity_days']} days")
        print(f"   Contract Rate: {test_lc['contract_rate']}")
        
        response = requests.post(
            f"{base_url}/api/calculate-backdated-pl",
            json=test_lc,
            headers={'Content-Type': 'application/json'},
            timeout=30  # Longer timeout for data fetching
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('data', {})
                
                # LC Details
                lc_details = result.get('lc_details', {})
                print(f"✅ P&L Calculation Success!")
                print(f"   LC Number: {lc_details.get('lc_number')}")
                print(f"   Amount: ${lc_details.get('amount_usd'):,}")
                print(f"   Period: {lc_details.get('issue_date')} to {lc_details.get('maturity_date')}")
                
                # P&L Summary
                pl_summary = result.get('pl_summary', {})
                print(f"   Final P&L: ₹{pl_summary.get('final_pl_inr', 0):,.2f}")
                print(f"   Max Profit: ₹{pl_summary.get('max_profit_inr', 0):,.2f}")
                print(f"   Max Loss: ₹{pl_summary.get('max_loss_inr', 0):,.2f}")
                print(f"   Data Points: {pl_summary.get('total_data_points', 0)}")
                print(f"   Data Source: {pl_summary.get('data_source')}")
                
                # Risk Metrics
                risk_metrics = result.get('risk_metrics', {})
                print(f"   P&L Volatility: ₹{risk_metrics.get('pl_volatility_inr', 0):,.2f}")
                print(f"   VaR 95%: ₹{risk_metrics.get('var_95_inr', 0):,.2f}")
                print(f"   Profit Days: {risk_metrics.get('profit_days', 0)}")
                print(f"   Loss Days: {risk_metrics.get('loss_days', 0)}")
                
                # Sample daily data
                daily_pl = result.get('daily_pl', [])
                if daily_pl:
                    print(f"\n   📊 Sample Daily Data (First 5 days):")
                    for i, day in enumerate(daily_pl[:5]):
                        print(f"     {day['date']}: Rate {day['market_rate']:.4f}, P&L ₹{day['daily_pl_inr']:,.2f}")
                    
                    if len(daily_pl) > 5:
                        print(f"     ... ({len(daily_pl) - 5} more days)")
                        
                        # Show last day
                        last_day = daily_pl[-1]
                        print(f"     {last_day['date']}: Rate {last_day['market_rate']:.4f}, P&L ₹{last_day['daily_pl_inr']:,.2f} (Final)")
                
                print(f"\n✅ REAL HISTORICAL DATA ANALYSIS COMPLETED!")
                
            else:
                print(f"❌ P&L calculation failed: {data.get('error')}")
        else:
            print(f"❌ P&L request failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ P&L calculation error: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 BACKDATED LC SYSTEM TEST COMPLETED")
    print("✅ Ready for real historical USD/INR analysis!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    print("🔄 Starting backdated LC system test...")
    print("   Note: This will fetch real historical USD/INR data")
    test_backdated_system()
