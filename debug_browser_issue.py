"""
Test current web browser API response to debug frontend issue
"""
import requests
import json

def test_current_browser_issue():
    """Test what the browser is actually receiving"""
    base_url = "http://127.0.0.1:5000"
    
    # Use the exact same data as the browser would send
    test_data = {
        "lc_number": "DEMO-LC-001",
        "amount_usd": 100000,
        "issue_date": "2025-07-01",  # Current date
        "maturity_date": "2025-09-29",  # 90 days from now
        "commodity": "Paddy Export",
        "beneficiary": "Export Company",
        "use_forward_rates": True
    }
    
    print("=" * 60)
    print("TESTING CURRENT BROWSER ISSUE")
    print("=" * 60)
    print(f"Test data: {test_data}")
    
    try:
        response = requests.post(f"{base_url}/api/calculate-pl", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"\nHTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                print(f"\n=== P&L RESULT STRUCTURE ===")
                for key, value in pl_result.items():
                    print(f"{key}: {value}")
                
                print(f"\n=== CHART DATA ===")
                chart_data = pl_result.get('chart_data', [])
                print(f"Chart data length: {len(chart_data)}")
                if chart_data:
                    print(f"First 3 points: {chart_data[:3]}")
                
                print(f"\n=== RISK METRICS ===")
                risk_metrics = data.get('risk_metrics', {})
                for key, value in risk_metrics.items():
                    print(f"{key}: {value}")
                    
            else:
                print(f"API Error: {data.get('error')}")
                if 'traceback' in data:
                    print(f"Traceback: {data['traceback']}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_current_browser_issue()
