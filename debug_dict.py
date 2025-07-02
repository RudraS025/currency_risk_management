#!/usr/bin/env python3
"""
Debug the exact issue step by step - check if it's in dictionary creation
"""

import yfinance as yf
import pandas as pd

# Get real data
ticker = yf.Ticker("USDINR=X")
data = ticker.history(start='2025-03-03', end='2025-03-10')

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
print(f"Real data DataFrame:")
print(real_df)
print(f"Type of real_df: {type(real_df)}")

# Test the dictionary creation line that might be problematic
print(f"\nTesting dictionary creation...")
try:
    # This line from the app:
    real_data_dict = {row['date']: row for _, row in real_df.iterrows()}
    print(f"Dictionary created successfully")
    print(f"Keys: {list(real_data_dict.keys())}")
    
    # Check what type the values are
    first_key = list(real_data_dict.keys())[0]
    first_value = real_data_dict[first_key]
    print(f"Type of dictionary value: {type(first_value)}")
    print(f"First value: {first_value}")
    
    # Test the problematic check
    print(f"\nTesting boolean check...")
    if first_value:
        print("✅ Boolean check passed")
    else:
        print("❌ Boolean check failed")
        
except Exception as e:
    print(f"❌ Error in dictionary creation: {e}")
    import traceback
    traceback.print_exc()
