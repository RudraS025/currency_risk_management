#!/usr/bin/env python3
"""
DIRECT FIX TEST - Bypass app.py and implement the fixed logic directly
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedHistoricalForexProvider:
    """FIXED version with proper pandas Series handling"""
    
    def get_historical_rates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get REAL USD/INR rates from Yahoo Finance with gap filling - FIXED VERSION"""
        try:
            logger.info(f"FIXED: Fetching REAL USD/INR data from Yahoo Finance: {start_date} to {end_date}")
            
            # Get real data from Yahoo Finance
            ticker = yf.Ticker("USDINR=X")
            data = ticker.history(start=start_date, end=end_date)
            
            if not data.empty:
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
                
                # Fill gaps for complete date coverage (weekends/holidays) - FIXED
                complete_df = self.fill_date_gaps_FIXED(real_df, start_date, end_date)
                
                logger.info(f"FIXED: REAL DATA from Yahoo Finance: {len(real_data)} trading days, {len(complete_df)} total days")
                return complete_df
            else:
                logger.warning("No real data available")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching real data: {e}")
            return pd.DataFrame()
    
    def fill_date_gaps_FIXED(self, real_df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """FIXED gap filling - no pandas Series boolean issues"""
        # Create complete date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # FIXED: Convert real data to dict properly - convert Series to dict
        real_data_dict = {}
        for _, row in real_df.iterrows():
            real_data_dict[row['date']] = row.to_dict()  # FIX: convert Series to dict
        
        complete_data = []
        last_known_rate = None
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            
            if date_str in real_data_dict:
                # Use real data
                row = real_data_dict[date_str]
                complete_data.append(row)
                last_known_rate = row
                print(f"REAL: {date_str} = ₹{row['close']}")
            else:
                # Fill gap with last known rate (forward fill)
                if last_known_rate is not None:  # FIX: proper None check
                    gap_row = {
                        'date': date_str,
                        'open': last_known_rate['close'],
                        'high': last_known_rate['close'],
                        'low': last_known_rate['close'],
                        'close': last_known_rate['close'],
                        'volume': 0  # Indicate this is gap-filled
                    }
                    complete_data.append(gap_row)
                    print(f"GAP FILL: {date_str} = ₹{gap_row['close']}")
        
        return pd.DataFrame(complete_data)

# TEST THE FIXED VERSION
if __name__ == "__main__":
    print("🔧 Testing FIXED HistoricalForexProvider...")
    
    fixed_provider = FixedHistoricalForexProvider()
    data = fixed_provider.get_historical_rates('2025-03-03', '2025-03-10')
    
    if len(data) > 0:
        print(f"\n✅ SUCCESS! Real data retrieved:")
        print(f"Data shape: {data.shape}")
        print(f"\nFirst few rates:")
        for i, row in data.head(5).iterrows():
            print(f"{row['date']}: ₹{row['close']}")
            
        print(f"\n🎯 Rate comparison:")
        print(f"Your table March 3: ₹85.2885 (synthetic)")
        print(f"FIXED March 3: ₹{data.iloc[0]['close']} (REAL)")
        print(f"Difference: ₹{data.iloc[0]['close'] - 85.2885:.4f}")
        
        if data.iloc[0]['close'] > 87:
            print("✅ SUCCESS: Using REAL Yahoo Finance data!")
        else:
            print("❌ STILL using synthetic data")
    else:
        print("❌ No data returned")
