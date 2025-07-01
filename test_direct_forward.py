"""
Test the ForwardPLCalculator directly to isolate issues
"""
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator

def test_forward_calculator_directly():
    """Test the ForwardPLCalculator in isolation"""
    print("=" * 60)
    print("TESTING FORWARD P&L CALCULATOR DIRECTLY")
    print("=" * 60)
    
    # Create the same LC as in web API test
    lc = LetterOfCredit(
        lc_id='DIRECT-TEST-001',
        commodity='Basmati Rice',
        quantity=1000,
        unit='tons',
        rate_per_unit=500.0,  # $500/ton * 1000 tons = $500,000
        currency='USD',
        signing_date='2024-01-01',
        maturity_days=90,  # 3 months
        customer_country='Test Country'
    )
    
    print(f"LC Details:")
    print(f"  ID: {lc.lc_id}")
    print(f"  Total Value: ${lc.total_value:,.2f}")
    print(f"  Signing Date: {lc.signing_date}")
    print(f"  Maturity Days: {lc.maturity_days}")
    print(f"  Days Remaining: {lc.days_remaining}")
    
    print(f"\nTesting ForwardPLCalculator...")
    
    try:
        calculator = ForwardPLCalculator()
        result = calculator.calculate_daily_forward_pl(lc, 'INR')
        
        print(f"Result type: {type(result)}")
        print(f"Result is None: {result is None}")
        
        if result:
            print(f"Result keys: {list(result.keys())}")
            
            # Check summary
            summary = result.get('summary', {})
            if summary:
                print(f"\nSummary:")
                print(f"  Current P&L: ₹{summary.get('current_pl', 0):,.2f}")
                print(f"  Max Profit: ₹{summary.get('max_profit', 0):,.2f}")
                print(f"  Max Loss: ₹{summary.get('max_loss', 0):,.2f}")
                print(f"  Max Profit Date: {summary.get('max_profit_date', 'N/A')}")
                print(f"  Max Loss Date: {summary.get('max_loss_date', 'N/A')}")
                print(f"  Volatility: {summary.get('volatility', 0):.4f}")
                print(f"  Total Days: {summary.get('total_days', 0)}")
            else:
                print("No summary data!")
            
            # Check chart data
            chart_data = result.get('chart_data', [])
            print(f"\nChart Data: {len(chart_data)} points")
            
            if chart_data:
                print("First 3 data points:")
                for i, point in enumerate(chart_data[:3]):
                    print(f"  {i+1}: {point}")
            
            # Check forward rates
            signing_rate = result.get('signing_forward_rate', 0)
            current_rate = result.get('current_forward_rate', 0)
            print(f"\nForward Rates:")
            print(f"  Signing Rate: {signing_rate:.4f}")
            print(f"  Current Rate: {current_rate:.4f}")
            
        else:
            print("❌ ForwardPLCalculator returned None!")
            
    except Exception as e:
        print(f"❌ Exception in ForwardPLCalculator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forward_calculator_directly()
