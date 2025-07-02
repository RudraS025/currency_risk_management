#!/usr/bin/env python3
import sys
import os
os.chdir('d:\\Currency_Risk_Management')

from app_fixed import HistoricalForexProvider, ForwardRatePLCalculator, RBIRateProvider

print('=== TESTING FIXED VERSION ===')

forex_provider = HistoricalForexProvider()
calculator = ForwardRatePLCalculator()
rbi_provider = RBIRateProvider()

# Test complete data fetching
print('\n1. Testing complete data fetching...')
historical_data = forex_provider.get_historical_rates('2025-01-01', '2025-06-02')
print(f'   Shape: {historical_data.shape}')
print(f'   First date: {historical_data.iloc[0]["date"]}')
print(f'   Last date: {historical_data.iloc[-1]["date"]}')

# Test contract rate calculation
first_day = historical_data.iloc[0]
spot_rate = first_day['close']
maturity_days = 152
interest_rate = rbi_provider.get_rbi_repo_rate()
forward_rate = calculator.calculate_forward_rate(spot_rate, maturity_days, interest_rate)

print(f'\n2. Contract rate (first day):')
print(f'   Date: {first_day["date"]}')
print(f'   Spot: {spot_rate:.4f}')
print(f'   Forward: {forward_rate:.4f}')

# Validation
first_ok = historical_data.iloc[0]['date'] == '2025-01-01'
last_ok = historical_data.iloc[-1]['date'] == '2025-06-02'
days_ok = len(historical_data) == 153

print(f'\n3. Results:')
print(f'   ✓ First date: {first_ok} ({historical_data.iloc[0]["date"]})')
print(f'   ✓ Last date: {last_ok} ({historical_data.iloc[-1]["date"]})')
print(f'   ✓ Days: {days_ok} ({len(historical_data)})')

if first_ok and last_ok and days_ok:
    print(f'\n🎉 FIXED! Contract rate will be {forward_rate:.4f}')
else:
    print(f'\n❌ Still issues')
