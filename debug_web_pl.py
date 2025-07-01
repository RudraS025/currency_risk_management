"""
Focused test to debug P&L calculation in web API
"""
import requests
import json

def test_pl_calculation():
    """Test P&L calculation with detailed debug"""
    base_url = "http://127.0.0.1:5000"
    
    test_data = {
        "lc_number": "DEBUG-001",
        "amount_usd": 500000,
        "issue_date": "2024-01-01",
        "maturity_date": "2024-04-01",
        "beneficiary": "Debug Exporter",
        "commodity": "Basmati Rice"
    }
    
    print("Testing P&L Calculation with detailed analysis...")
    
    try:
        response = requests.post(f"{base_url}/api/calculate-pl", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                print("\nP&L Results:")
                print(f"  Total P&L (INR): ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"  Current Rate: {pl_result.get('spot_rate', 0):.4f}")
                print(f"  Original Rate: {pl_result.get('original_rate', 0):.4f}")
                print(f"  P&L Percentage: {pl_result.get('pl_percentage', 0):.2f}%")
                print(f"  Days Remaining: {pl_result.get('days_remaining', 0)}")
                print(f"  Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"  Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"  Max Profit Date: {pl_result.get('max_profit_date', 'N/A')}")
                print(f"  Max Loss Date: {pl_result.get('max_loss_date', 'N/A')}")
                print(f"  Volatility: {pl_result.get('volatility', 0):.4f}")
                print(f"  Chart Data Points: {len(pl_result.get('chart_data', []))}")
                
                # Analyze if forward rates are being used
                if pl_result.get('chart_data'):
                    print("\n✅ Chart data available - Forward rates likely being used")
                    sample_points = pl_result.get('chart_data', [])[:3]  # First 3 points
                    for i, point in enumerate(sample_points):
                        print(f"    Point {i+1}: Date={point.get('date', 'N/A')}, P&L=₹{point.get('pl', 0):,.2f}")
                else:
                    print("\n⚠️  No chart data - Might be using fallback calculation")
                
                # Check risk metrics
                risk_metrics = data.get('risk_metrics', {})
                print(f"\nRisk Metrics:")
                print(f"  VaR (95%): ₹{risk_metrics.get('var_95', 0):,.2f}")
                print(f"  Volatility: {risk_metrics.get('volatility', 0):.4f}")
                
            else:
                print(f"API returned error: {data.get('error', 'Unknown error')}")
                if 'traceback' in data:
                    print(f"Traceback: {data['traceback']}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_pl_calculation()
