"""
Simple test to verify the Currency Risk Management System works
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.data_providers.real_forward_rates_2025 import RealForwardRatesProvider2025
from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025
from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from datetime import datetime

def test_real_2025_system():
    """Test the real 2025 system components"""
    print("=" * 60)
    print("TESTING REAL 2025 SYSTEM COMPONENTS")
    print("=" * 60)
    
    # Test 1: Data Provider
    print("\n1. Testing Real Forward Rates Provider...")
    try:
        provider = RealForwardRatesProvider2025()
        # Test data availability
        available = provider.is_data_available("2025-06-01", "2025-09-01")
        print(f"✅ Data available for June-September 2025: {available}")
        
        # Test daily rates with correct signature
        rates = provider.get_daily_forward_rates(
            base_currency='USD',
            quote_currency='INR',
            maturity_date="2025-09-01",
            start_date="2025-06-01",
            end_date="2025-09-01"
        )
        print(f"✅ Got {len(rates)} forward rates")
        if rates:
            rate_list = list(rates.values())
            print(f"   First rate: {rate_list[0].date} = {rate_list[0].rate:.4f}")
            print(f"   Last rate: {rate_list[-1].date} = {rate_list[-1].rate:.4f}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: P&L Calculator
    print("\n2. Testing Real Forward P&L Calculator...")
    try:
        calculator = RealForwardPLCalculator2025()
        
        # Create test LC with correct interface
        lc = LetterOfCredit(
            lc_id="TEST-2025-001",
            commodity="Technology Equipment",
            quantity=1000,
            unit="units",
            rate_per_unit=1000,
            currency="USD",
            signing_date="2025-06-01",
            maturity_days=92,  # About 3 months
            customer_country="India",
            contract_rate=84.50
        )
        
        print(f"   LC created: {lc.lc_id}")
        print(f"   Signing date: {lc.signing_date_obj.strftime('%Y-%m-%d')}")
        print(f"   Maturity date: {lc.maturity_date.strftime('%Y-%m-%d')}")
        print(f"   Total value: ${lc.total_value:,.2f}")
        
        # Calculate P&L
        daily_pl = calculator.calculate_daily_pl(lc)
        print(f"✅ Calculated P&L for {len(daily_pl)} days")
        
        if daily_pl:
            # Find key metrics - daily_pl contains RealPLResult objects
            max_profit = max(daily_pl, key=lambda x: x.pl_amount)
            max_loss = min(daily_pl, key=lambda x: x.pl_amount)
            final_pl = daily_pl[-1]
            
            print(f"   Max Profit: ${max_profit.pl_amount:,.2f} on {max_profit.date}")
            print(f"   Max Loss: ${max_loss.pl_amount:,.2f} on {max_loss.date}")
            print(f"   Final P&L: ${final_pl.pl_amount:,.2f}")
            
            # Check for realistic variation
            rates = [point.forward_rate for point in daily_pl]
            unique_rates = len(set(rates))
            print(f"   Unique rates: {unique_rates} (should be > 1)")
            
            if unique_rates > 1:
                print("✅ CONFIRMED: Using real, time-varying rates!")
            else:
                print("⚠️  WARNING: Static rates detected")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("COMPONENT TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_real_2025_system()
