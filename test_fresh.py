#!/usr/bin/env python3
"""
Fresh test with explicit module reload to avoid caching
"""

import importlib
import sys

# Clear any cached modules
if 'app' in sys.modules:
    del sys.modules['app']

# Import fresh
from app import HistoricalForexProvider
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, force=True)

# Test the provider
print("Testing HistoricalForexProvider with fresh import...")
provider = HistoricalForexProvider()

# Test with a smaller date range first
print("Testing smaller date range 2025-03-03 to 2025-03-04...")
try:
    data = provider.get_historical_rates('2025-03-03', '2025-03-04')
    
    print(f"\nSuccess! Returned data shape: {data.shape}")
    print(f"First row:")
    if len(data) > 0:
        print(f"Date: {data.iloc[0]['date']}")
        print(f"Close: ₹{data.iloc[0]['close']}")
        print(f"Is this real data? {data.iloc[0]['close'] > 87}")  # Real data should be ~87.46
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
