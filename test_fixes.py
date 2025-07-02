#!/usr/bin/env python3
"""
Test the fixes for contract rate calculation and table completeness
"""

import requests
import json
from datetime import datetime, timedelta

def test_fixes():
    print('Testing contract rate suggestion and table completeness fixes...')
    try:
        from app import HistoricalForexProvider, ForwardRatePLCalculator, RBIRateProvider

        forex_provider = HistoricalForexProvider()
        calculator = ForwardRatePLCalculator()
        rbi_provider = RBIRateProvider()

        # Test the historical data fetching for the problematic date range
        print('Testing historical data fetching for 2025-01-01 to 2025-06-02...')
        historical_data = forex_provider.get_historical_rates('2025-01-01', '2025-06-02')
        print(f'Historical data shape: {historical_data.shape}')
        print(f'Expected days: {(datetime(2025, 6, 2) - datetime(2025, 1, 1)).days + 1} days')
        
        print(f'\nFirst 5 rows:')
        print(historical_data.head(5))
        print(f'\nLast 5 rows:')
        print(historical_data.tail(5))

        # Test first day contract rate calculation
        first_day = historical_data.iloc[0]
        spot_rate = first_day['close']
        maturity_days = 152  # 2025-01-01 to 2025-06-02
        interest_rate = rbi_provider.get_rbi_repo_rate()
        forward_rate = calculator.calculate_forward_rate(spot_rate, maturity_days, interest_rate)

        print(f'\nFirst day calculation:')
        print(f'Date: {first_day["date"]}')
        print(f'Spot rate: {spot_rate:.4f}')
        print(f'Maturity days: {maturity_days}')
        print(f'Interest rate: {interest_rate}%')
        print(f'Forward rate (suggested contract rate): {forward_rate:.4f}')

        # Check if the first and last dates are correct
        expected_first = '2025-01-01'
        expected_last = '2025-06-02'
        actual_first = historical_data.iloc[0]['date']
        actual_last = historical_data.iloc[-1]['date']
        
        print(f'\nDate range validation:')
        print(f'Expected first date: {expected_first}, Actual: {actual_first} ✓' if actual_first == expected_first else f'Expected first date: {expected_first}, Actual: {actual_first} ✗')
        print(f'Expected last date: {expected_last}, Actual: {actual_last} ✓' if actual_last == expected_last else f'Expected last date: {expected_last}, Actual: {actual_last} ✗')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fixes()
