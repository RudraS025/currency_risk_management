#!/usr/bin/env python3
"""
Forward Rates P&L Demo - Shows daily forward rates analysis
This demonstrates the advanced forward rates P&L calculation your client requested.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, timedelta
from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
import pandas as pd

def demonstrate_forward_pl():
    """Demonstrate forward rates P&L calculation"""
    
    print("=" * 70)
    print("FORWARD RATES P&L ANALYSIS - Advanced Currency Risk Management")
    print("=" * 70)
    
    # Create LC - Your Paddy Export
    lc = LetterOfCredit(
        lc_id="PADDY-IRAN-FORWARD-001",
        commodity="Basmati Rice (Paddy)",
        quantity=1000.0,
        unit="tons",
        rate_per_unit=400.0,  # $400 per ton = $400,000 total
        currency="USD",
        signing_date="2025-06-16",  # Signed 14 days ago
        maturity_days=90,  # 90 days from signing
        customer_country="Iran",
        incoterm="FOB",
        port_of_loading="Mumbai", 
        description="Premium Basmati Rice Export with Forward Rate Analysis"
    )
    
    print(f"\n📋 LETTER OF CREDIT DETAILS:")
    print(f"   LC ID: {lc.lc_id}")
    print(f"   Amount: ${lc.total_value:,.2f} USD")
    print(f"   Commodity: {lc.commodity}")
    print(f"   Signed: {lc.signing_date}")
    print(f"   Maturity: {lc.maturity_date.strftime('%Y-%m-%d')}")
    print(f"   Days Remaining: {lc.days_remaining}")
    
    # Initialize forward P&L calculator
    forward_calculator = ForwardPLCalculator()
    
    print(f"\n🔮 FORWARD RATES CONCEPT:")
    print(f"   Forward rates show what the market expects USD/INR to be")
    print(f"   on your LC maturity date ({lc.maturity_date.strftime('%Y-%m-%d')})")
    print(f"   These rates change daily based on market expectations")
    print(f"   Your P&L changes based on these forward expectations")
    
    # Generate forward P&L report
    print(f"\n📊 GENERATING FORWARD P&L ANALYSIS...")
    forward_report = forward_calculator.generate_forward_pl_report(lc, "INR")
    
    if forward_report and forward_report.get('daily_forward_pl'):
        print(f"\n✅ FORWARD RATES ANALYSIS COMPLETED")
        
        # Show current status
        current_status = forward_report.get('current_status', {})
        if current_status:
            print(f"\n📈 CURRENT FORWARD RATE STATUS:")
            print(f"   Date: {current_status.get('current_date', 'N/A')}")
            print(f"   Forward Rate for Maturity: ₹{current_status.get('current_forward_rate', 0):.4f}")
            print(f"   Expected Value at Maturity: ₹{current_status.get('expected_value_at_maturity', 0):,.2f}")
            print(f"   Forward P&L: ₹{current_status.get('unrealized_pl', 0):,.2f}")
            print(f"   Forward P&L %: {current_status.get('pl_percentage', 0):.2f}%")
            print(f"   Days to Maturity: {current_status.get('days_to_maturity', 0)}")
        
        # Show daily forward rates (last 7 days)
        daily_pl = forward_report['daily_forward_pl']
        recent_dates = sorted(daily_pl.keys())[-7:]  # Last 7 days
        
        print(f"\n📅 DAILY FORWARD RATES (Last 7 Days):")
        print(f"   {'Date':<12} {'Forward Rate':<12} {'Expected Value':<15} {'Daily P&L':<12} {'P&L %':<8}")
        print(f"   {'-'*65}")
        
        for date in recent_dates:
            data = daily_pl[date]
            print(f"   {date:<12} ₹{data['forward_rate']:<11.4f} "
                  f"₹{data['expected_value_at_maturity']:<14,.0f} "
                  f"₹{data['unrealized_pl']:<11,.0f} {data['pl_percentage']:<7.2f}%")
        
        # Show scenarios
        hold_scenario = forward_report.get('hold_to_maturity_scenario', {})
        if hold_scenario:
            print(f"\n🎯 HOLD TO MATURITY SCENARIO:")
            print(f"   If you hold till maturity ({hold_scenario.get('maturity_date', 'N/A')}):")
            print(f"   Expected Forward Rate: ₹{hold_scenario.get('current_forward_rate', 0):.4f}")
            print(f"   Expected Value: ₹{hold_scenario.get('current_expected_value', 0):,.2f}")
            print(f"   Forward P&L: ₹{hold_scenario.get('unrealized_pl', 0):,.2f}")
            print(f"   Forward P&L %: {hold_scenario.get('pl_percentage', 0):.2f}%")
        
        # Show exit scenarios
        exit_scenarios = forward_report.get('exit_scenarios', [])
        if exit_scenarios:
            print(f"\n🚪 EARLY EXIT SCENARIOS:")
            print(f"   {'Exit Date':<12} {'Days Held':<10} {'Exit Value':<15} {'P&L':<12} {'P&L %':<8}")
            print(f"   {'-'*60}")
            
            for scenario in exit_scenarios:
                print(f"   {scenario.get('exit_date', 'N/A'):<12} "
                      f"{scenario.get('days_held', 0):<10} "
                      f"₹{scenario.get('exit_value', 0):<14,.0f} "
                      f"₹{scenario.get('unrealized_pl', 0):<11,.0f} "
                      f"{scenario.get('pl_percentage', 0):<7.2f}%")
        
        # Show analysis
        analysis = forward_report.get('analysis', {})
        if analysis:
            print(f"\n🔍 FORWARD RATE ANALYSIS:")
            print(f"   Trend: {analysis.get('forward_rate_trend', 'N/A').replace('_', ' ').title()}")
            print(f"   Volatility: {analysis.get('volatility', 0):.4f}")
            print(f"   Recommendation: {analysis.get('recommendation', 'N/A').replace('_', ' ').title()}")
            print(f"   Days Tracked: {analysis.get('total_days_tracked', 0)}")
        
        # Explain what this means
        print(f"\n💡 WHAT FORWARD RATES MEAN FOR YOU:")
        if current_status.get('unrealized_pl', 0) > 0:
            print(f"   ✅ Market expects USD to STRENGTHEN by maturity")
            print(f"   ✅ You're expected to receive MORE INR")
            print(f"   ✅ Forward market is favorable to your position")
        elif current_status.get('unrealized_pl', 0) < 0:
            print(f"   ⚠️  Market expects USD to WEAKEN by maturity")
            print(f"   ⚠️  You're expected to receive LESS INR")
            print(f"   ⚠️  Forward market is unfavorable to your position")
        else:
            print(f"   ➡️  Market expects NO CHANGE by maturity")
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   1. Forward rates show MARKET EXPECTATIONS, not guarantees")
        print(f"   2. Your P&L changes daily based on these expectations")
        print(f"   3. You can exit early at spot rates or hold for forward rates")
        print(f"   4. Forward P&L helps you make informed hedging decisions")
        print(f"   5. Banks/agencies provide these forward rates daily")
        
        # Save report
        try:
            import json
            with open("forward_pl_report.json", "w") as f:
                json.dump(forward_report, f, indent=2, default=str)
            print(f"\n💾 Detailed report saved as: forward_pl_report.json")
        except Exception as e:
            print(f"\n❌ Could not save report: {e}")
    
    else:
        print(f"\n❌ FORWARD RATES ANALYSIS UNAVAILABLE")
        print(f"   This could be due to:")
        print(f"   - Limited historical data")
        print(f"   - API connectivity issues")
        print(f"   - Weekend/holiday data gaps")
        print(f"   ")
        print(f"   Note: In production, you would connect to:")
        print(f"   - Bank forward rate feeds")
        print(f"   - Bloomberg/Reuters APIs")
        print(f"   - Central bank forward curve data")
    
    print(f"\n" + "=" * 70)

def show_forward_rates_concept():
    """Explain forward rates concept with examples"""
    
    print(f"\n🎓 FORWARD RATES CONCEPT EXPLAINED:")
    print(f"   " + "=" * 50)
    
    print(f"\n📚 What are Forward Rates?")
    print(f"   Forward rates are what the market thinks the exchange rate")
    print(f"   will be on a specific future date (your LC maturity date)")
    
    print(f"\n📊 Example Scenario:")
    print(f"   Your LC: $400,000 maturing on 2025-09-14")
    print(f"   ")
    print(f"   June 16, 2025 (Signing): Forward rate for Sep 14 = ₹86.25")
    print(f"   June 17, 2025: Forward rate for Sep 14 = ₹86.50")
    print(f"   June 18, 2025: Forward rate for Sep 14 = ₹86.10")
    print(f"   ... and so on daily")
    
    print(f"\n💰 P&L Calculation:")
    print(f"   Original expectation: $400,000 × ₹86.25 = ₹3,45,00,000")
    print(f"   June 17 expectation: $400,000 × ₹86.50 = ₹3,46,00,000")
    print(f"   Forward P&L: ₹3,46,00,000 - ₹3,45,00,000 = +₹1,00,000")
    
    print(f"\n🎯 Business Decisions:")
    print(f"   1. EXIT EARLY: Sell USD at current spot rate")
    print(f"   2. HOLD: Wait for maturity and get forward rate")
    print(f"   3. HEDGE: Lock in current forward rate")
    print(f"   4. MONITOR: Track daily changes and decide")
    
    print(f"\n🏦 Data Sources (Real Implementation):")
    print(f"   - Bank forward rate desks")
    print(f"   - Bloomberg Terminal")
    print(f"   - Reuters Eikon")
    print(f"   - Central Bank forward curves")
    print(f"   - FX trading platforms")

if __name__ == "__main__":
    demonstrate_forward_pl()
    show_forward_rates_concept()
    
    print(f"\n💡 TIP: This advanced analysis helps you make sophisticated")
    print(f"   currency risk decisions based on market expectations!")
    print(f"   Run this daily to track how forward expectations change.")
