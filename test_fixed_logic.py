#!/usr/bin/env python3
"""
Test our exact fixed logic in isolation
"""

import yfinance as yf
import pandas as pd

def test_fixed_gap_filling():
    start_date = '2025-03-03'
    end_date = '2025-03-10'
    
    # Get real data
    ticker = yf.Ticker("USDINR=X")
    data = ticker.history(start=start_date, end=end_date)
    
    # Convert to our format
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
    print(f"Real data: {len(real_data)} rows")
    
    # Test the FIXED gap filling logic
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # FIXED: Convert real data to dict properly
    real_data_dict = {}
    for _, row in real_df.iterrows():
        real_data_dict[row['date']] = row.to_dict()
    
    print(f"Dictionary created with {len(real_data_dict)} entries")
    print(f"Sample dict entry type: {type(list(real_data_dict.values())[0])}")
    
    complete_data = []
    last_known_rate = None
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"Processing {date_str}")
        
        if date_str in real_data_dict:
            row = real_data_dict[date_str]
            complete_data.append(row)
            last_known_rate = row
            print(f"  -> Real data: ₹{row['close']}")
        else:
            # FIXED: Use 'is not None' instead of boolean check
            if last_known_rate is not None:
                gap_row = {
                    'date': date_str,
                    'open': last_known_rate['close'],
                    'high': last_known_rate['close'],
                    'low': last_known_rate['close'],
                    'close': last_known_rate['close'],
                    'volume': 0
                }
                complete_data.append(gap_row)
                print(f"  -> Gap filled: ₹{gap_row['close']}")
            else:
                print(f"  -> Skipped (no last rate)")
    
    final_df = pd.DataFrame(complete_data)
    print(f"\nFinal result:")
    print(final_df[['date', 'close']])
    return final_df

if __name__ == "__main__":
    result = test_fixed_gap_filling()
