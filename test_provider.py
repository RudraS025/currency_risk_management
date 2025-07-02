#!/usr/bin/env python3
"""
Test the actual HistoricalForexProvider to see what data it's returning
"""

import sys
sys.path.append('.')

from app import HistoricalForexProvider
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test the provider
provider = HistoricalForexProvider()

# Test with the date range from your data
print("Testing HistoricalForexProvider with March 2025 dates...")
data = provider.get_historical_rates('2025-03-03', '2025-03-10')

print(f"\nReturned data shape: {data.shape}")
print(f"First few rows:")
print(data.head(10))

print(f"\nRate comparison:")
print(f"Your table March 3: ₹85.2885")
print(f"Provider March 3: ₹{data.iloc[0]['close']}")
print(f"Difference: ₹{data.iloc[0]['close'] - 85.2885:.4f}")

print(f"\nAll March 3-10 close rates:")
for i, row in data.head(8).iterrows():
    print(f"{row['date']}: ₹{row['close']}")
