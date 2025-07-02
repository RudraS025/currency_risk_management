#!/usr/bin/env python3
"""
Final test of the complete fix
"""

import os
import sys

# Remove app from cache if it exists
if 'app' in sys.modules:
    del sys.modules['app']

# Change to the correct directory and test
os.chdir('d:\\Currency_Risk_Management')

# Now import fresh
from app import HistoricalForexProvider, ForwardRatePLCalculator, RBIRateProvider

def final_test():
    print("=== FINAL TEST: Complete Fix Verification ===")
    
    # Test the complete data flow
    forex_provider = HistoricalForexProvider()
    calculator = ForwardRatePLCalculator()
    rbi_provider = RBIRateProvider()
    
    # Test the historical data fetching for the problematic date range
    print('\n1. Testing complete data fetching for 2025-01-01 to 2025-06-02...')
    historical_data = forex_provider.get_historical_rates('2025-01-01', '2025-06-02')
    
    print(f'   Historical data shape: {historical_data.shape}')
    print(f'   Expected days: 153 days')
    print(f'   First date: {historical_data.iloc[0]["date"]}')
    print(f'   Last date: {historical_data.iloc[-1]["date"]}')
    
    # Test first day contract rate calculation
    first_day = historical_data.iloc[0]
    spot_rate = first_day['close']
    maturity_days = 152  # 2025-01-01 to 2025-06-02
    interest_rate = rbi_provider.get_rbi_repo_rate()
    forward_rate = calculator.calculate_forward_rate(spot_rate, maturity_days, interest_rate)
    
    print(f'\n2. Contract rate calculation (first day):')
    print(f'   Date: {first_day["date"]}')
    print(f'   Spot rate: {spot_rate:.4f}')
    print(f'   Maturity days: {maturity_days}')
    print(f'   Interest rate: {interest_rate}%')
    print(f'   Forward rate (suggested contract rate): {forward_rate:.4f}')
    
    # Validation checks
    expected_first = '2025-01-01'
    expected_last = '2025-06-02'
    actual_first = historical_data.iloc[0]['date']
    actual_last = historical_data.iloc[-1]['date']
    
    print(f'\n3. Validation Results:')
    first_ok = actual_first == expected_first
    last_ok = actual_last == expected_last
    days_ok = len(historical_data) == 153
    
    print(f'   ✓ First date correct: {first_ok} ({actual_first} == {expected_first})')
    print(f'   ✓ Last date correct: {last_ok} ({actual_last} == {expected_last})')
    print(f'   ✓ Day count correct: {days_ok} ({len(historical_data)} == 153)')
    
    if first_ok and last_ok and days_ok:
        print(f'\n🎉 ALL ISSUES FIXED! The table will now show:')
        print(f'   - Complete date range from {expected_first} to {expected_last}')
        print(f'   - Contract rate will be {forward_rate:.4f} (forward rate of first day)')
        print(f'   - All 153 days will be displayed in the table')
    else:
        print(f'\n❌ Issues still exist')
    
    return first_ok and last_ok and days_ok

if __name__ == '__main__':
    success = final_test()
    if success:
        print(f'\n✅ Ready to deploy!')
    else:
        print(f'\n❌ Need more fixes')
