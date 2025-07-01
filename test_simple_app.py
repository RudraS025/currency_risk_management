"""
Test the simple 2025 app.
"""

import requests

def test_simple_app():
    """Test the simple app."""
    
    try:
        response = requests.get("http://127.0.0.1:5001/api/test-real-2025", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Test App Results:")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Data Source: {result.get('data_source', 'N/A')}")
            print(f"   LC Amount: ${result.get('lc_amount', 0):,.2f}")
            print(f"   Contract Rate: {result.get('contract_rate', 0):.4f}")
            print(f"   Final Forward Rate: {result.get('final_forward_rate', 0):.4f}")
            print(f"   Final P&L: ${result.get('final_pl', 0):,.2f}")
            print(f"   P&L Percentage: {result.get('pl_percentage', 0):.2f}%")
            print(f"   Data Points: {result.get('data_points', 0)}")
            
            if result.get('success') and result.get('data_source') == 'Real_2025_Market_Data':
                print("\n🎉 SUCCESS: Real 2025 data is working perfectly!")
                return True
            else:
                print(f"\n❌ ISSUE: {result.get('message', 'Unknown issue')}")
                return False
                
        else:
            print(f"❌ Test failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_app()
