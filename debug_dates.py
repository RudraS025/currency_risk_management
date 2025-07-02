#!/usr/bin/env python3
"""
Debug the date range issue
"""

from datetime import datetime, timedelta

def debug_dates():
    print("Debug date range issue...")
    
    # Test dates
    start_date = '2025-01-01'
    end_date = '2025-06-02'
    today = datetime.now().date()
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    print(f"Start date: {start_date} ({start_dt.date()})")
    print(f"End date: {end_date} ({end_dt.date()})")
    print(f"Today: {today}")
    print(f"End date is in future? {end_dt.date() > today}")
    print(f"Expected days: {(end_dt - start_dt).days + 1}")
    
    # Test synthetic data generation
    from app import HistoricalForexProvider
    provider = HistoricalForexProvider()
    
    print("\nTesting synthetic data generation...")
    synthetic_data = provider.generate_synthetic_data(start_date, end_date)
    print(f"Synthetic data shape: {synthetic_data.shape}")
    print(f"First date: {synthetic_data.iloc[0]['date']}")
    print(f"Last date: {synthetic_data.iloc[-1]['date']}")
    
    # Test the full historical data fetch
    print("\nTesting full historical data fetch...")
    historical_data = provider.get_historical_rates(start_date, end_date)
    print(f"Historical data shape: {historical_data.shape}")
    print(f"First date: {historical_data.iloc[0]['date']}")
    print(f"Last date: {historical_data.iloc[-1]['date']}")

if __name__ == '__main__':
    debug_dates()
