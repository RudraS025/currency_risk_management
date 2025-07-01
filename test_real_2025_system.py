"""
Test script to verify the Real 2025 Forward Rates system is working correctly.
Tests the actual LC scenario with real forward rates data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025
from currency_risk_mgmt.data_providers.real_forward_rates_2025 import RealForwardRatesProvider2025
from datetime import datetime

def test_real_2025_data():
    """Test the real 2025 forward rates system."""
    
    print("="*80)
    print("TESTING REAL 2025 FORWARD RATES SYSTEM")
    print("="*80)
    
    # Test the data provider first
    print("\n1. Testing RealForwardRatesProvider2025...")
    provider = RealForwardRatesProvider2025()
    
    # Check data coverage
    coverage = provider.get_data_coverage()
    print(f"   Data Coverage: {coverage['start_date']} to {coverage['end_date']}")
    print(f"   Total Days: {coverage['total_days']}")
    print(f"   Currency Pair: {coverage['currency_pair']}")
    print(f"   Source: {coverage['source']}")
    
    # Test individual rate lookup
    test_date = "2025-06-16"
    maturity_date = "2025-09-16"
    rate_obj = provider.get_forward_rate(test_date, maturity_date)
    
    if rate_obj:
        print(f"   Sample Rate ({test_date}): {rate_obj.rate:.4f}")
        print(f"   Days to Maturity: {rate_obj.days_to_maturity}")
        print(f"   Confidence: {rate_obj.confidence}")
    else:
        print(f"   ERROR: No rate found for {test_date}")
        return False
    
    # Test daily rates series
    daily_rates = provider.get_daily_forward_rates(
        'USD', 'INR', maturity_date, test_date, '2025-06-20'
    )
    print(f"   Daily rates (5 days): {len(daily_rates)} rates retrieved")
    
    for date, rate_obj in list(daily_rates.items())[:3]:  # Show first 3
        print(f"     {date}: {rate_obj.rate:.4f}")
    
    print("   ✓ Data Provider Test PASSED")
    
    # Test the P&L calculator
    print("\n2. Testing RealForwardPLCalculator2025...")
    calculator = RealForwardPLCalculator2025()
    
    # Create a real LC for June-September 2025
    lc = LetterOfCredit(
        lc_id='REAL-LC-2025-001',
        commodity='Electronics Export',
        quantity=1000,
        unit='units',
        rate_per_unit=500.0,  # $500 per unit
        currency='USD',
        signing_date='2025-06-16',
        maturity_days=92,  # June 16 to Sep 16 = 92 days
        customer_country='USA'
    )
    
    print(f"   LC Details:")
    print(f"     LC ID: {lc.lc_id}")
    print(f"     Amount: ${lc.total_value:,.2f}")
    print(f"     Issue Date: {lc.signing_date}")
    print(f"     Maturity Date: {lc.maturity_date}")
    print(f"     Contract Rate: {lc.contract_rate:.4f}")
    
    # Check if real data is available
    data_available = calculator.is_real_data_available('2025-06-16', '2025-09-16')
    print(f"   Real Data Available: {data_available}")
    
    if not data_available:
        print("   ERROR: Real data not available for LC dates")
        return False
    
    # Calculate daily P&L
    print("\n3. Calculating Daily P&L...")
    daily_pl = calculator.calculate_daily_pl(lc, '2025-06-16')
    
    if not daily_pl:
        print("   ERROR: No P&L results calculated")
        return False
    
    print(f"   P&L Results: {len(daily_pl)} daily calculations")
    
    # Show sample results
    print("   Sample P&L Results:")
    for i, pl in enumerate(daily_pl[:5]):  # First 5 days
        print(f"     {pl.date}: Rate={pl.forward_rate:.4f}, P&L=${pl.pl_amount:,.2f}, Days={pl.days_to_maturity}")
    
    # Show final result
    final_pl = daily_pl[-1]
    print(f"   Final Result ({final_pl.date}):")
    print(f"     Forward Rate: {final_pl.forward_rate:.4f}")
    print(f"     P&L Amount: ${final_pl.pl_amount:,.2f}")
    print(f"     P&L Percentage: {final_pl.pl_percentage:.2f}%")
    
    # Calculate scenario analysis
    print("\n4. Testing Scenario Analysis...")
    scenarios = calculator.calculate_scenario_analysis(lc, '2025-06-16')
    
    if scenarios:
        print(f"   Scenarios Generated: {len(scenarios)}")
        print("   Key Scenarios:")
        for scenario in scenarios[:5]:  # Show first 5
            print(f"     {scenario.scenario_name}: Final P&L=${scenario.final_pl:,.2f}")
    else:
        print("   ERROR: No scenarios generated")
        return False
    
    # Calculate risk metrics
    print("\n5. Testing Risk Metrics...")
    risk_metrics = calculator.get_risk_metrics(lc, '2025-06-16')
    
    if risk_metrics:
        print("   Risk Metrics:")
        print(f"     Max Profit: ${risk_metrics['max_profit']:,.2f}")
        print(f"     Max Loss: ${risk_metrics['max_loss']:,.2f}")
        print(f"     VaR 95%: ${risk_metrics['var_95']:,.2f}")
        print(f"     Rate Volatility: {risk_metrics['rate_volatility']:.4f}")
        print(f"     P&L Volatility: ${risk_metrics['pl_volatility']:,.2f}")
    else:
        print("   ERROR: No risk metrics calculated")
        return False
    
    # Find optimal dates
    print("\n6. Testing Optimal Dates...")
    optimal_dates = calculator.find_optimal_dates(lc, '2025-06-16')
    
    if optimal_dates:
        print("   Optimal Dates:")
        for key, (date, amount) in optimal_dates.items():
            print(f"     {key}: {date} (${amount:,.2f})")
    else:
        print("   ERROR: No optimal dates found")
        return False
    
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED - REAL 2025 SYSTEM IS WORKING!")
    print("="*80)
    
    # Summary
    print(f"\nSUMMARY FOR REAL LC (June 16 - September 16, 2025):")
    print(f"  LC Amount: ${lc.total_value:,.2f}")
    print(f"  Contract Rate: {lc.contract_rate:.4f}")
    print(f"  Final Forward Rate: {final_pl.forward_rate:.4f}")
    print(f"  Total P&L: ${final_pl.pl_amount:,.2f}")
    print(f"  P&L Percentage: {final_pl.pl_percentage:.2f}%")
    print(f"  Max Profit Potential: ${risk_metrics['max_profit']:,.2f}")
    print(f"  Max Loss Risk: ${risk_metrics['max_loss']:,.2f}")
    print(f"  Data Source: Real Market Forward Rates")
    
    return True

if __name__ == "__main__":
    try:
        success = test_real_2025_data()
        if success:
            print("\n🎉 SUCCESS: The Real 2025 system is ready for production!")
        else:
            print("\n❌ FAILURE: Issues found in the Real 2025 system")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
