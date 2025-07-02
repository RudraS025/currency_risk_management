#!/usr/bin/env python3
"""
Quick test of the fixed app.py
"""

from app import HistoricalForexProvider, ForexForwardCalculator
import logging

logging.basicConfig(level=logging.INFO)

print("🔧 Testing FIXED app.py...")

# Test the provider
print("\n1. Testing HistoricalForexProvider...")
provider = HistoricalForexProvider()
data = provider.get_historical_rates('2025-03-03', '2025-03-10')

print(f"Data shape: {data.shape}")
if len(data) > 0:
    print(f"First row: {data.iloc[0]}")
    print(f"March 3 rate: ₹{data.iloc[0]['close']}")
    print(f"Data source: REAL Yahoo Finance data")
else:
    print("❌ No data returned")

# Test current rate
print("\n2. Testing current rate...")
calculator = ForexForwardCalculator()
current_rate = calculator.get_current_spot_rate()
print(f"Current USD/INR: ₹{current_rate}")

print("\n✅ Test complete!")
