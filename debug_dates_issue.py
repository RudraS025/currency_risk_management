"""
Test ForwardPLCalculator with current browser dates to isolate the issue
"""
import sys
import os
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator

def test_current_dates_issue():
    """Test with exact current browser dates"""
    print("=" * 60)
    print("TESTING FORWARD P&L WITH CURRENT DATES")
    print("=" * 60)
    
    # Create LC with current browser dates (issue: today, maturity: 89 days)
    today = datetime.now()
    maturity = today + timedelta(days=89)
    
    issue_date = today.strftime("%Y-%m-%d")
    maturity_date = maturity.strftime("%Y-%m-%d")
    
    print(f"Issue Date: {issue_date}")
    print(f"Maturity Date: {maturity_date}")
    print(f"Days: {(maturity - today).days}")
    
    lc = LetterOfCredit(
        lc_id='CURRENT-DATE-TEST',
        commodity='Test Commodity',
        quantity=1000,
        unit='tons',
        rate_per_unit=100.0,  # $100/ton * 1000 = $100,000
        currency='USD',
        signing_date=issue_date,
        maturity_days=89,
        customer_country='Test Country'
    )
    
    print(f"\nLC Created:")
    print(f"  Total Value: ${lc.total_value:,.2f}")
    print(f"  Days Remaining: {lc.days_remaining}")
    
    # Test ForwardPLCalculator
    calculator = ForwardPLCalculator()
    result = calculator.calculate_daily_forward_pl(lc, 'INR')
    
    print(f"\nResult type: {type(result)}")
    print(f"Result keys: {list(result.keys()) if result else 'None'}")
    
    if result:
        summary = result.get('summary', {})
        chart_data = result.get('chart_data', [])
        
        print(f"\nSummary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print(f"\nChart data points: {len(chart_data)}")
        if chart_data:
            print(f"First few points:")
            for i, point in enumerate(chart_data[:3]):
                print(f"  {i+1}: {point}")
    else:
        print("❌ ForwardPLCalculator returned empty result!")
        
    # Now test with historical dates (like our previous working tests)
    print(f"\n" + "=" * 60)
    print("TESTING WITH HISTORICAL DATES (WORKING CASE)")
    print("=" * 60)
    
    historical_issue = "2024-01-01"
    historical_maturity = "2024-04-01"
    
    lc_historical = LetterOfCredit(
        lc_id='HISTORICAL-TEST',
        commodity='Test Commodity',
        quantity=1000,
        unit='tons',
        rate_per_unit=100.0,
        currency='USD',
        signing_date=historical_issue,
        maturity_days=90,
        customer_country='Test Country'
    )
    
    print(f"Historical LC:")
    print(f"  Issue: {historical_issue}")
    print(f"  Maturity: {historical_maturity}")
    print(f"  Days Remaining: {lc_historical.days_remaining}")
    
    result_historical = calculator.calculate_daily_forward_pl(lc_historical, 'INR')
    
    if result_historical:
        summary_hist = result_historical.get('summary', {})
        chart_data_hist = result_historical.get('chart_data', [])
        
        print(f"\nHistorical Summary:")
        for key, value in summary_hist.items():
            print(f"  {key}: {value}")
        
        print(f"\nHistorical chart data points: {len(chart_data_hist)}")
    else:
        print("❌ Historical test also failed!")

if __name__ == "__main__":
    test_current_dates_issue()
