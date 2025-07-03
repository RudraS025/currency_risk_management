#!/usr/bin/env python3
"""
Test script for date format fix
"""
from datetime import datetime

def convert_date_format(date_str):
    """Convert DD-MM-YYYY to YYYY-MM-DD if needed"""
    if '-' in date_str and len(date_str.split('-')[0]) == 2:
        day, month, year = date_str.split('-')
        return f"{year}-{month}-{day}"
    return date_str

# Test the problematic dates
issue_original = "04-03-2025"
maturity_original = "03-06-2025"

print(f"Original issue date: {issue_original}")
print(f"Original maturity date: {maturity_original}")

issue_converted = convert_date_format(issue_original)
maturity_converted = convert_date_format(maturity_original)

print(f"Converted issue date: {issue_converted}")
print(f"Converted maturity date: {maturity_converted}")

issue_date = datetime.strptime(issue_converted, '%Y-%m-%d')
maturity_date = datetime.strptime(maturity_converted, '%Y-%m-%d')

print(f"Parsed issue date: {issue_date}")
print(f"Parsed maturity date: {maturity_date}")

days_diff = (maturity_date - issue_date).days
print(f"Days difference: {days_diff}")

if maturity_date <= issue_date:
    print("❌ ERROR: Maturity date is before or equal to issue date!")
else:
    print("✅ SUCCESS: Dates are valid")
    
    # Test forward rate calculation
    spot_rate = 85.6
    import math
    
    if days_diff > 0:
        r = 6.5 / 100  # RBI rate
        forward_rate = spot_rate * math.exp((r / 365) * days_diff)
        contract_rate = forward_rate + 0.5  # Add buffer
        
        print(f"Spot rate: ₹{spot_rate}")
        print(f"Forward rate: ₹{forward_rate:.4f}")
        print(f"Suggested contract rate: ₹{contract_rate:.4f}")
    else:
        print("❌ ERROR: Invalid days difference")
