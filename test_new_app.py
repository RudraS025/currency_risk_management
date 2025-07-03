#!/usr/bin/env python3
"""
Test the new complete app.py
"""

try:
    import app
    print("✅ App import successful")
    
    # Check available classes
    classes = [c for c in dir(app) if c[0].isupper()]
    print(f"Available classes: {classes}")
    
    # Test the calculator
    if hasattr(app, 'calculator'):
        print("✅ Calculator available")
        current_rate = app.calculator.get_current_spot_rate()
        print(f"Current USD/INR rate: ₹{current_rate}")
    else:
        print("❌ Calculator not found")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
