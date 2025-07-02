#!/usr/bin/env python3
"""
Test the gap filling logic specifically
"""

import sys
sys.path.append('.')

import yfinance as yf
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gap_filling():
    start_date = '2025-03-03'
    end_date = '2025-03-10'
    
    # Get real data first
    ticker = yf.Ticker("USDINR=X")
    data = ticker.history(start=start_date, end=end_date)
    
    # Convert to our format (same as in app)
    real_data = []
    for date, row in data.iterrows():
        real_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(float(row['Open']), 4),
            'high': round(float(row['High']), 4),
            'low': round(float(row['Low']), 4),
            'close': round(float(row['Close']), 4),
            'volume': int(row['Volume']) if pd.notna(row['Volume']) else 1000000
        })
    
    real_df = pd.DataFrame(real_data)
    print(f"Real data before gap filling:")
    print(real_df)
    
    # Now test the gap filling logic
    print(f"\nTesting gap filling logic...")
    
    # Create complete date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    print(f"Complete date range: {len(dates)} days")
    
    # Convert real data to dict for easy lookup
    real_data_dict = {row['date']: row for _, row in real_df.iterrows()}
    print(f"Real data dict keys: {list(real_data_dict.keys())}")
    
    complete_data = []
    last_known_rate = None
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"Processing date: {date_str}")
        
        if date_str in real_data_dict:
            # Use real data
            row = real_data_dict[date_str]
            complete_data.append(row)
            last_known_rate = row
            print(f"  -> Using real data: ₹{row['close']}")
        else:
            # Fill gap with last known rate (forward fill)
            if last_known_rate:
                gap_row = {
                    'date': date_str,
                    'open': last_known_rate['close'],
                    'high': last_known_rate['close'],
                    'low': last_known_rate['close'],
                    'close': last_known_rate['close'],
                    'volume': 0  # Indicate this is gap-filled
                }
                complete_data.append(gap_row)
                print(f"  -> Gap filled: ₹{gap_row['close']}")
            else:
                print(f"  -> Skipped (no last known rate)")
    
    final_df = pd.DataFrame(complete_data)
    print(f"\nFinal data after gap filling:")
    print(final_df[['date', 'close']])
    
    return final_df

if __name__ == "__main__":
    result = test_gap_filling()
