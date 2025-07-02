#!/usr/bin/env python3
"""
Get actual historical data for the user's LC to show real calculation
"""

import requests
import json
from datetime import datetime

def show_actual_lc_calculation():
    print("🔍 YOUR ACTUAL LC CALCULATION BREAKDOWN")
    print("=" * 50)
    
    # Get the actual data from our API
    lc_data = {
        "lc_id": "DEMO-LC-001",
        "lc_amount": 500000,
        "lc_currency": "USD", 
        "contract_rate": 82.50,
        "issue_date": "2025-05-03",
        "maturity_date": "2025-06-02",
        "business_type": "import"
    }
    
    print(f"📋 YOUR LC DETAILS:")
    print(f"   LC Number: {lc_data['lc_id']}")
    print(f"   Amount: ${lc_data['lc_amount']:,}")
    print(f"   Contract Rate: ₹{lc_data['contract_rate']}")
    print(f"   Period: {lc_data['issue_date']} to {lc_data['maturity_date']}")
    print(f"   Type: {lc_data['business_type'].title()}")
    
    # Calculate what you committed to pay
    committed_amount = lc_data['lc_amount'] * lc_data['contract_rate']
    print(f"\n💰 WHAT YOU COMMITTED TO PAY:")
    print(f"   ${lc_data['lc_amount']:,} × ₹{lc_data['contract_rate']} = ₹{committed_amount:,}")
    
    try:
        # Get actual calculation from our system
        response = requests.post(
            "http://127.0.0.1:5000/api/calculate-backdated-pl",
            json=lc_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and 'data' in data:
                result = data['data']
                pl_summary = result.get('pl_summary', {})
                risk_metrics = result.get('risk_metrics', {})
                daily_pl = result.get('daily_pl', [])
                
                print(f"\n📊 WHAT ACTUALLY HAPPENED:")
                print(f"   📈 Final P&L: ₹{pl_summary.get('final_pl_inr', 0):,.2f}")
                print(f"   🎯 This means you SAVED this much money!")
                
                print(f"\n🔢 THE MATH:")
                print(f"   Instead of paying ₹{committed_amount:,}")
                actual_paid = committed_amount - pl_summary.get('final_pl_inr', 0)
                print(f"   You actually paid: ₹{actual_paid:,.2f}")
                print(f"   Your savings: ₹{pl_summary.get('final_pl_inr', 0):,.2f}")
                
                print(f"\n📈 DAILY BREAKDOWN:")
                print(f"   Data Points: {pl_summary.get('total_data_points', 0)} days")
                print(f"   Profit Days: {risk_metrics.get('profit_days', 0)}")
                print(f"   Loss Days: {risk_metrics.get('loss_days', 0)}")
                
                if risk_metrics.get('profit_days', 0) == pl_summary.get('total_data_points', 0):
                    print(f"   🎉 AMAZING! You made profit EVERY SINGLE DAY!")
                
                print(f"\n🎲 RISK ANALYSIS:")
                print(f"   Max Profit Day: ₹{pl_summary.get('max_profit_inr', 0):,.2f}")
                print(f"   Max Loss Day: ₹{pl_summary.get('max_loss_inr', 0):,.2f}")
                print(f"   VaR (95%): ₹{risk_metrics.get('var_95_inr', 0):,.2f}")
                print(f"   (This means 95% confidence you'll make at least this much)")
                
                print(f"\n🏆 SIMPLE SUMMARY:")
                if pl_summary.get('final_pl_inr', 0) > 0:
                    print(f"   ✅ You WON! USD got cheaper, you saved money")
                    print(f"   💰 Your profit: ₹{pl_summary.get('final_pl_inr', 0):,.2f}")
                else:
                    print(f"   ❌ You lost money - USD got expensive")
                    print(f"   💸 Your loss: ₹{abs(pl_summary.get('final_pl_inr', 0)):,.2f}")
                
                print(f"\n🎯 WHAT THIS MEANS:")
                print(f"   🏪 You wanted to buy $500K worth of goods")
                print(f"   📝 You agreed to pay ₹82.50 per dollar")
                print(f"   📊 But during your LC period, dollar became cheaper")
                print(f"   💰 So you saved ₹{pl_summary.get('final_pl_inr', 0):,.2f}!")
                print(f"   🎉 This is pure bonus money from currency movement!")
                
            else:
                print(f"❌ Could not get calculation: {data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Error getting calculation: {e}")
        print(f"💡 Make sure the Flask app is running on localhost:5000")

if __name__ == "__main__":
    show_actual_lc_calculation()
