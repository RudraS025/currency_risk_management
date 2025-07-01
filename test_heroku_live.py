"""
Test the live Heroku deployment
"""
import requests
import json

def test_heroku_deployment():
    """Test the live Heroku deployment"""
    base_url = "https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com"
    
    print("=" * 60)
    print("TESTING LIVE HEROKU DEPLOYMENT")
    print(f"URL: {base_url}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data.get('status', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Current Rates
    print("\n2. Testing Current Rates API...")
    try:
        response = requests.get(f"{base_url}/api/current-rates", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Rate: {data.get('rate', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: P&L Calculation
    print("\n3. Testing P&L Calculation API...")
    test_data = {
        "lc_number": "HEROKU-TEST-001",
        "amount_usd": 500000,
        "issue_date": "2024-01-01",
        "maturity_date": "2024-04-01",
        "beneficiary": "Live Test Exporter",
        "commodity": "Export Goods"
    }
    
    try:
        response = requests.post(f"{base_url}/api/calculate-pl", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                print(f"✅ P&L Calculation Success!")
                print(f"   Current P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"   Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"   Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"   Chart Data Points: {len(pl_result.get('chart_data', []))}")
                
                if abs(pl_result.get('total_pl_inr', 0)) > 1000 and len(pl_result.get('chart_data', [])) > 0:
                    print("🚀 HEROKU DEPLOYMENT WORKING PERFECTLY!")
                else:
                    print("⚠️  Results seem limited - check logs")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "=" * 60)
    print("HEROKU DEPLOYMENT TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_heroku_deployment()
