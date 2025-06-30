#!/usr/bin/env python3
"""
P&L Calculation Explanation with Simple Examples
This script demonstrates how the Currency Risk Management System calculates P&L
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, timedelta
from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider

def demonstrate_pl_calculation():
    """Demonstrate P&L calculation with clear examples"""
    
    print("=" * 60)
    print("CURRENCY RISK MANAGEMENT - P&L CALCULATION EXPLAINED")
    print("=" * 60)
    
    # Create a sample LC - Paddy export to Iran
    lc = LetterOfCredit(
        lc_id="PADDY-IRAN-001",
        commodity="Basmati Rice (Paddy)",
        quantity=1000.0,  # 1000 tons
        unit="tons",
        rate_per_unit=100.0,  # $100 per ton = $100,000 total
        currency="USD",
        signing_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),  # Signed 30 days ago
        maturity_days=90,  # 90 days total maturity
        customer_country="Iran",
        incoterm="FOB",
        port_of_loading="Mumbai",
        port_of_discharge="Bandar Abbas",
        description="Premium Basmati Rice Export to Iran"
    )
    
    print(f"\n📋 LETTER OF CREDIT DETAILS:")
    print(f"   LC ID: {lc.lc_id}")
    print(f"   Amount: ${lc.total_value:,.2f} USD")
    print(f"   Commodity: {lc.commodity}")
    print(f"   Signed: {lc.signing_date} ({lc.days_elapsed} days ago)")
    print(f"   Maturity: {lc.maturity_date.strftime('%Y-%m-%d')} ({lc.days_remaining} days remaining)")
    
    # Calculate P&L
    print(f"\n💰 P&L CALCULATION PROCESS:")
    print(f"   Step 1: Get exchange rate when LC was signed")
    print(f"   Step 2: Get current exchange rate")
    print(f"   Step 3: Calculate value in INR at both rates")
    print(f"   Step 4: Calculate profit/loss difference")
    
    # Initialize calculators
    pl_calculator = ProfitLossCalculator()
    
    # Get current P&L
    pl_result = pl_calculator.calculate_current_pl(lc, "INR")
    
    if pl_result and pl_result.get('unrealized_pl') is not None:
        print(f"\n📊 DETAILED P&L BREAKDOWN:")
        print(f"   Foreign Currency Amount: ${pl_result['lc_value_foreign']:,.2f} USD")
        print(f"   Exchange Rate at Signing: ₹{pl_result['signing_rate']:.4f} per USD")
        print(f"   Current Exchange Rate: ₹{pl_result['current_rate']:.4f} per USD")
        print(f"   ")
        print(f"   Value in INR at Signing: ₹{pl_result['lc_value_base_at_signing']:,.2f}")
        print(f"   Value in INR Today: ₹{pl_result['lc_value_base_current']:,.2f}")
        print(f"   ")
        print(f"   💡 PROFIT/LOSS CALCULATION:")
        print(f"   Unrealized P&L = Current Value - Signing Value")
        print(f"   Unrealized P&L = ₹{pl_result['lc_value_base_current']:,.2f} - ₹{pl_result['lc_value_base_at_signing']:,.2f}")
        print(f"   Unrealized P&L = ₹{pl_result['unrealized_pl']:,.2f}")
        print(f"   ")
        print(f"   📈 PERFORMANCE METRICS:")
        print(f"   P&L Percentage: {pl_result['pl_percentage']:.2f}%")
        print(f"   Daily P&L: ₹{pl_result['daily_pl']:,.2f} per day")
        print(f"   Days Active: {pl_result['days_elapsed']} days")
        
        # Explain what this means
        print(f"\n🎯 WHAT THIS MEANS:")
        if pl_result['unrealized_pl'] > 0:
            print(f"   ✅ FAVORABLE: USD has strengthened against INR")
            print(f"   ✅ You will receive MORE INR when you convert USD")
            print(f"   ✅ Currency movement is in your favor by ₹{abs(pl_result['unrealized_pl']):,.2f}")
        elif pl_result['unrealized_pl'] < 0:
            print(f"   ⚠️  UNFAVORABLE: USD has weakened against INR")
            print(f"   ⚠️  You will receive LESS INR when you convert USD")
            print(f"   ⚠️  Currency movement is against you by ₹{abs(pl_result['unrealized_pl']):,.2f}")
        else:
            print(f"   ➡️  NEUTRAL: No change in exchange rate")
        
        print(f"\n🔍 RISK ANALYSIS:")
        risk_level = "LOW" if abs(pl_result['pl_percentage']) < 2 else "MEDIUM" if abs(pl_result['pl_percentage']) < 5 else "HIGH"
        print(f"   Risk Level: {risk_level}")
        print(f"   Daily Volatility: ₹{abs(pl_result['daily_pl']):,.2f}")
        print(f"   Remaining Exposure: {pl_result['days_remaining']} days")
        
        # Show calculation formula
        print(f"\n📝 CALCULATION FORMULAS:")
        print(f"   Value at Signing = USD Amount × Signing Rate")
        print(f"   Value at Signing = ${pl_result['lc_value_foreign']:,.2f} × {pl_result['signing_rate']:.4f} = ₹{pl_result['lc_value_base_at_signing']:,.2f}")
        print(f"   ")
        print(f"   Current Value = USD Amount × Current Rate")
        print(f"   Current Value = ${pl_result['lc_value_foreign']:,.2f} × {pl_result['current_rate']:.4f} = ₹{pl_result['lc_value_base_current']:,.2f}")
        print(f"   ")
        print(f"   Unrealized P&L = Current Value - Signing Value")
        print(f"   P&L % = (Unrealized P&L ÷ Signing Value) × 100")
        print(f"   Daily P&L = Unrealized P&L ÷ Days Elapsed")
        
    else:
        print(f"\n❌ Could not calculate P&L - forex data unavailable")
        print(f"   This might be due to:")
        print(f"   - API rate limits")
        print(f"   - Network connectivity issues")
        print(f"   - Weekend/holiday data gaps")
    
    print(f"\n" + "=" * 60)

def show_example_scenarios():
    """Show different P&L scenarios with hypothetical rates"""
    
    print(f"\n🎭 EXAMPLE SCENARIOS (Hypothetical Rates):")
    print(f"   LC Amount: $100,000 USD")
    print(f"   " + "-" * 50)
    
    scenarios = [
        {"name": "Favorable Scenario", "signing_rate": 82.50, "current_rate": 83.25, "description": "USD strengthened"},
        {"name": "Unfavorable Scenario", "signing_rate": 82.50, "current_rate": 81.75, "description": "USD weakened"},
        {"name": "Neutral Scenario", "signing_rate": 82.50, "current_rate": 82.50, "description": "No change"},
        {"name": "High Volatility", "signing_rate": 82.50, "current_rate": 85.00, "description": "Major USD gain"}
    ]
    
    for scenario in scenarios:
        signing_value = 100000 * scenario["signing_rate"]
        current_value = 100000 * scenario["current_rate"]
        pl = current_value - signing_value
        pl_percent = (pl / signing_value) * 100
        
        print(f"\n   📊 {scenario['name']}:")
        print(f"      Signing Rate: ₹{scenario['signing_rate']:.2f} per USD")
        print(f"      Current Rate: ₹{scenario['current_rate']:.2f} per USD")
        print(f"      P&L: ₹{pl:,.2f} ({pl_percent:+.2f}%)")
        print(f"      Impact: {scenario['description']}")

if __name__ == "__main__":
    demonstrate_pl_calculation()
    show_example_scenarios()
    
    print(f"\n💡 TIP: Run this script regularly to monitor your LC's P&L performance!")
    print(f"   The system automatically fetches live exchange rates for accurate calculations.")
