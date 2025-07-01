"""
Test the fixed web application with historical dates
"""
import requests
import json

def test_fixed_web_app():
    """Test the web app with historical dates for meaningful results"""
    base_url = "http://127.0.0.1:5000"
    
    # Use historical dates that provide rich data
    test_data = {
        "lc_number": "DEMO-LC-001",
        "amount_usd": 500000,  # $500K for visible results
        "issue_date": "2024-01-01",  # Historical start
        "maturity_date": "2024-04-01",  # 3 months later
        "commodity": "Paddy Export",
        "beneficiary": "Export Company",
        "use_forward_rates": True
    }
    
    print("=" * 60)
    print("TESTING FIXED WEB APPLICATION")
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
                
                print(f"\n✅ P&L RESULTS:")
                print(f"  Total P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"  Current Rate: ₹{pl_result.get('spot_rate', 0):.4f}")
                print(f"  Original Rate: ₹{pl_result.get('original_rate', 0):.4f}")
                print(f"  P&L %: {pl_result.get('pl_percentage', 0):.2f}%")
                print(f"  Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"  Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"  Volatility: ₹{pl_result.get('volatility', 0):,.2f}")
                
                chart_data = pl_result.get('chart_data', [])
                print(f"\n📊 CHART DATA:")
                print(f"  Data Points: {len(chart_data)}")
                
                if chart_data and len(chart_data) > 5:
                    print(f"  ✅ MEANINGFUL CHART DATA AVAILABLE!")
                    print(f"  Sample points:")
                    for i, point in enumerate(chart_data[:3]):
                        print(f"    {i+1}: Date={point.get('date')}, P&L=₹{point.get('pl', 0):,.2f}")
                elif chart_data:
                    print(f"  ⚠️  Limited chart data: {chart_data}")
                else:
                    print(f"  ❌ No chart data")
                
                # Check if we got meaningful values
                total_pl = abs(pl_result.get('total_pl_inr', 0))
                max_profit = abs(pl_result.get('max_profit', 0))
                max_loss = abs(pl_result.get('max_loss', 0))
                
                if total_pl > 1000 and max_profit > 1000 and len(chart_data) > 10:
                    print(f"\n🎉 SUCCESS! WEB APPLICATION IS NOW WORKING!")
                    print(f"   - Meaningful P&L values: ✅")
                    print(f"   - Rich chart data: ✅")
                    print(f"   - Max profit/loss: ✅")
                else:
                    print(f"\n❌ Still showing limited results")
                    
            else:
                print(f"❌ API Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fixed_web_app()
