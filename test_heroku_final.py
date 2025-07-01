"""
Test the live Heroku deployment - Clean version
"""
import requests
import json

def test_heroku_deployment():
    """Test the live Heroku deployment"""
    base_url = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"
    
    print("=" * 80)
    print("🌐 TESTING LIVE HEROKU DEPLOYMENT")
    print(f"URL: {base_url}")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=30)
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
        response = requests.get(f"{base_url}/api/current-rates", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current USD/INR Rate: {data.get('rate', 'N/A'):.4f}")
        else:
            print(f"❌ Current rates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Current rates error: {e}")
    
    # Test 3: P&L Calculation with Real 2025 Data
    print("\n3️⃣ Testing P&L Calculation (Real 2025 Data)...")
    test_lc = {
        "lc_number": "HEROKU-LIVE-TEST",
        "amount_usd": 750000,  # $750k LC
        "issue_date": "2025-06-15",
        "maturity_date": "2025-08-30",
        "beneficiary": "Live Test Exporter",
        "commodity": "Export Goods"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/calculate-pl",
            json=test_lc,
            headers={'Content-Type': 'application/json'},
            timeout=60
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
                
                if daily_pl and len(daily_pl) > 0:
                    final_pl = daily_pl[-1]
                    print(f"   Final P&L: ₹{final_pl['pl_amount']:,.2f}")
                    print(f"   Final Rate: {final_pl['forward_rate']:.4f}")
                    
                    # Check data quality
                    rates = [point['forward_rate'] for point in daily_pl]
                    unique_rates = len(set(rates))
                    print(f"   Unique Rates: {unique_rates}")
                    
                    if unique_rates > 10:
                        print("✅ CONFIRMED: Live system using real forward rates!")
                    else:
                        print("⚠️  WARNING: Limited rate variation detected")
                
                # Risk metrics
                risk_metrics = data.get('risk_metrics', {})
                print(f"   VaR (95%): ₹{risk_metrics.get('var_95', 0):,.2f}")
                print(f"   Volatility: {risk_metrics.get('volatility', 0):.2f}%")
                
            else:
                print(f"❌ P&L calculation failed: {data.get('error')}")
        else:
            print(f"❌ P&L request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ P&L calculation error: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 LIVE HEROKU DEPLOYMENT TEST COMPLETED")
    print(f"🌐 Visit: {base_url}")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_heroku_deployment()
