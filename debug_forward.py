#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator

def debug_forward_calculation():
    print("🔍 DEBUGGING FORWARD P&L CALCULATION")
    print("=" * 50)
    
    # Create test LC
    lc = LetterOfCredit(
        lc_id='DEBUG-001',
        commodity='Rice',
        quantity=1000,
        unit='MT',
        rate_per_unit=150,
        currency='USD',
        signing_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        maturity_days=90,
        customer_country='Test'
    )
    
    print(f"LC Details:")
    print(f"  ID: {lc.lc_id}")
    print(f"  Amount: ${lc.total_value:,}")
    print(f"  Signing Date: {lc.signing_date}")
    print(f"  Maturity Date: {lc.maturity_date.strftime('%Y-%m-%d')}")
    print(f"  Days Remaining: {lc.days_remaining}")
    print()
    
    # Test forward calculator
    print("Testing Forward P&L Calculator...")
    calculator = ForwardPLCalculator()
    
    try:
        result = calculator.calculate_daily_forward_pl(lc, 'INR')
        
        if result:
            print(f"✅ Forward calculation returned data")
            print(f"  Result keys: {list(result.keys())}")
            
            summary = result.get('summary', {})
            if summary:
                print(f"  Summary keys: {list(summary.keys())}")
                print(f"  Current P&L: ₹{summary.get('current_pl', 0):,.2f}")
                print(f"  Max Profit: ₹{summary.get('max_profit', 0):,.2f}")
                print(f"  Total Days: {summary.get('total_days', 0)}")
            else:
                print("  ❌ No summary data")
                
            print(f"  Signing Rate: ₹{result.get('signing_forward_rate', 0):.4f}")
            print(f"  Current Rate: ₹{result.get('current_forward_rate', 0):.4f}")
            print(f"  Chart Data Points: {len(result.get('chart_data', []))}")
            
            daily_pl = result.get('daily_pl', {})
            if daily_pl:
                print(f"  Daily P&L entries: {len(daily_pl)}")
                # Show first few entries
                for i, (date, data) in enumerate(sorted(daily_pl.items())[:3]):
                    print(f"    {date}: Rate=₹{data.get('forward_rate', 0):.4f}, P&L=₹{data.get('unrealized_pl', 0):,.2f}")
                    if i >= 2:
                        break
            else:
                print("  ❌ No daily P&L data")
                
        else:
            print("❌ Forward calculation returned empty result")
            
    except Exception as e:
        print(f"❌ Forward calculation failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🔍 DEBUGGING SUMMARY")
    print("-" * 30)
    if result and result.get('summary', {}).get('current_pl', 0) != 0:
        print("✅ Forward calculation is working correctly")
        print("✅ P&L values are meaningful")
        print("🚀 The app should now show proper results")
    else:
        print("❌ Forward calculation is still not working")
        print("🔧 Need to investigate further")

if __name__ == "__main__":
    debug_forward_calculation()
