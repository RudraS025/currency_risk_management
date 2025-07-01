"""
Quick test to see what the web API actually returns
"""
import requests
import json

def test_api_response():
    """Test what the API actually returns"""
    base_url = "http://localhost:5000"
    
    # Test P&L calculation
    test_data = {
        "lc_number": "API-TEST-001",
        "amount_usd": 500000,
        "issue_date": "2025-06-01",
        "maturity_date": "2025-09-01",
        "beneficiary": "Test Exporter",
        "commodity": "Technology Equipment"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/calculate-pl",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print("Status Code:", response.status_code)
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_response()
