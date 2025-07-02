#!/usr/bin/env python3
"""
Test the complete fix with fresh imports
"""

import sys
import importlib

def test_complete_fix():
    print("Testing complete fix with fresh imports...")
    
    # Force reload of the app module
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    
    from app import HistoricalForexProvider, ForwardRatePLCalculator, RBIRateProvider
    
    # Test the complete data flow
    forex_provider = HistoricalForexProvider()
    calculator = ForwardRatePLCalculator()
    rbi_provider = RBIRateProvider()
    
    # Test the historical data fetching for the problematic date range
    print('Testing complete data fetching for 2025-01-01 to 2025-06-02...')
    historical_data = forex_provider.get_historical_rates('2025-01-01', '2025-06-02')
    print(f'Historical data shape: {historical_data.shape}')
    print(f'Expected days: 153 days')
    
    print(f'\nFirst 3 rows:')
    print(historical_data.head(3))
    print(f'\nLast 3 rows:')
    print(historical_data.tail(3))
    
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
    print(f'Expected days: 153, Actual: {len(historical_data)} ✓' if len(historical_data) == 153 else f'Expected days: 153, Actual: {len(historical_data)} ✗')

if __name__ == '__main__':
    test_complete_fix()
