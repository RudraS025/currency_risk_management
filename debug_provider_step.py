#!/usr/bin/env python3
"""
Test the exact HistoricalForexProvider logic step by step
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_provider_logic():
    start_date = '2025-03-03'
    end_date = '2025-03-10'
    
    try:
        logger.info(f"Fetching REAL USD/INR data from Yahoo Finance: {start_date} to {end_date}")
        
        # Get real data from Yahoo Finance
        ticker = yf.Ticker("USDINR=X")
        data = ticker.history(start=start_date, end=end_date)
        
        print(f"Data received: {type(data)}")
        print(f"Data shape: {data.shape}")
        print(f"Is empty: {data.empty}")
        
        # The problematic line
        print("Testing 'if not data.empty:'...")
        
        if not data.empty:
            print("✅ Data is not empty - proceeding with conversion")
            
            # Convert to our format
            real_data = []
            for date, row in data.iterrows():
                converted_row = {
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(float(row['Open']), 4),
                    'high': round(float(row['High']), 4),
                    'low': round(float(row['Low']), 4),
                    'close': round(float(row['Close']), 4),
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) else 1000000
                }
                real_data.append(converted_row)
                print(f"Converted {converted_row['date']}: ₹{converted_row['close']}")
            
            real_df = pd.DataFrame(real_data)
            print(f"Real data DataFrame shape: {real_df.shape}")
            
            return real_df
            
        else:
            print("❌ Data is empty - would use fallback")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = test_provider_logic()
