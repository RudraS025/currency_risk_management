#!/usr/bin/env python3
"""
Quick P&L Examples - No user input required
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'interactive_pl_calculator.py'))

from interactive_pl_calculator import calculate_pl_scenario, print_scenario_result

def show_quick_examples():
    """Show quick P&L examples"""
    
    print("💱 QUICK P&L EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            'title': 'Your Paddy Export Example',
            'description': 'Current live scenario from your system',
            'usd_amount': 100000,
            'signing_rate': 85.3613,
            'current_rate': 85.7170,
            'days_elapsed': 30
        },
        {
            'title': 'Unfavorable Scenario',
            'description': 'What if USD had weakened instead',
            'usd_amount': 100000,
            'signing_rate': 85.3613,
            'current_rate': 84.50,
            'days_elapsed': 30
        },
        {
            'title': 'High Volatility',
            'description': 'Major currency movement',
            'usd_amount': 100000,
            'signing_rate': 82.00,
            'current_rate': 86.00,
            'days_elapsed': 45
        }
    ]
    
    for example in examples:
        print(f"\n🔹 {example['title']}")
        print(f"   {example['description']}")
        
        result = calculate_pl_scenario(
            example['usd_amount'],
            example['signing_rate'], 
            example['current_rate'],
            example['days_elapsed']
        )
        
        print_scenario_result(result)
        print("\n" + "="*60)

if __name__ == "__main__":
    show_quick_examples()
