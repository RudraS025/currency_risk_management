#!/usr/bin/env python3
"""
Test Flask endpoints of fixed app
"""

import requests
import time
import threading
from app import app

def test_endpoints():
    """Test the Flask endpoints"""
    try:
        print("🌐 Testing Flask endpoints...")
        
        # Test current rates
        print("\n1. Testing /api/current-rates")
        response = requests.get('http://localhost:5001/api/current-rates', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
            if 'Yahoo Finance' in data.get('rates', {}).get('source', ''):
                print("✅ Using real Yahoo Finance data!")
            else:
                print("❌ Still using synthetic/demo data")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # Test historical rates
        print("\n2. Testing /api/historical-rates")
        response = requests.get('http://localhost:5001/api/historical-rates?start_date=2025-03-03&end_date=2025-03-05', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Got {data['data']['count']} records")
            print(f"Source: {data['data']['source']}")
            if 'Yahoo Finance' in data['data']['source']:
                print("✅ Using real Yahoo Finance data!")
            else:
                print("❌ Still using synthetic/demo data")
        else:
            print(f"❌ Error: {response.status_code}")
            
        # Test health
        print("\n3. Testing /health")
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data}")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

if __name__ == "__main__":
    # Start the app in a separate thread
    def run_app():
        app.run(port=5001, debug=False, use_reloader=False)
    
    print("🚀 Starting test server...")
    t = threading.Thread(target=run_app)
    t.daemon = True
    t.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Test endpoints
    test_endpoints()
    
    print("\n✅ API tests complete!")
