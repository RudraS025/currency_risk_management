"""
Quick test for the debug endpoint.
"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint."""
    
    base_url = "http://127.0.0.1:5000"
    
    test_data = {
        "test": "data",
        "issue_date": "2025-06-16",
        "maturity_date": "2025-09-16"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/test-debug",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Debug endpoint test:")
            print(f"  Success: {result.get('success')}")
            print(f"  Debug Info: {result.get('debug_info')}")
            return True
        else:
            print(f"Debug endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing debug endpoint: {e}")
        return False

if __name__ == "__main__":
    test_debug_endpoint()
