#!/usr/bin/env python3
"""
Debug the exact issue with Yahoo Finance data fetching
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

print("Testing Yahoo Finance data access...")

ticker = yf.Ticker("USDINR=X")
print(f"Ticker created: {ticker}")

try:
    print("Fetching data for 2025-03-03 to 2025-03-10...")
    data = ticker.history(start='2025-03-03', end='2025-03-10')
    
    print(f"Data type: {type(data)}")
    print(f"Data shape: {data.shape}")
    print(f"Data empty check: {data.empty}")
    print(f"Data columns: {list(data.columns)}")
    print(f"Data index: {data.index}")
    
    if len(data) > 0:
        print("\nFirst row:")
        print(data.iloc[0])
        
        print("\nConverting first row:")
        row = data.iloc[0]
        result = {
            'date': data.index[0].strftime('%Y-%m-%d'),
            'open': round(float(row['Open']), 4),
            'high': round(float(row['High']), 4),
            'low': round(float(row['Low']), 4),
            'close': round(float(row['Close']), 4),
            'volume': int(row['Volume']) if pd.notna(row['Volume']) else 1000000
        }
        print(f"Converted: {result}")
    else:
        print("No data returned!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
