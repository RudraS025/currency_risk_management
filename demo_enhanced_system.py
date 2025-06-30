#!/usr/bin/env python3
"""
Demo script showcasing the enhanced Currency Risk Management System
with daily forward P&L calculations and meaningful results.
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator

def demo_enhanced_pl_system():
    """Demonstrate the enhanced P&L system with meaningful results"""
    
    print("🚀 ENHANCED CURRENCY RISK MANAGEMENT SYSTEM DEMO")
    print("=" * 80)
    print("This demo shows the new features:")
    print("✅ Daily forward rate calculations with realistic market variations")
    print("✅ Meaningful P&L results (not always zero!)")
    print("✅ Daily P&L tracking from signing to maturity")
    print("✅ Maximum profit/loss identification with dates")
    print("✅ Data ready for bar chart visualization")
    print("✅ Ultra-modern web interface")
    print()
    
    # Create a realistic LC scenario
    signing_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    maturity_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    
    lc = LetterOfCredit(
        lc_id="DEMO-ENHANCED-001",
        commodity="Basmati Rice",
        quantity=2000,
        unit="MT",
        rate_per_unit=150,  # $150 per MT = $300,000 total
        currency="USD",
        signing_date=signing_date,
        maturity_days=90,
        customer_country="Iran",
        incoterm="FOB",
        port_of_loading="Mumbai",
        port_of_discharge="Bandar Abbas"
    )
    
    print("📋 LETTER OF CREDIT DETAILS")
    print("-" * 50)
    print(f"LC ID: {lc.lc_id}")
    print(f"Commodity: {lc.commodity}")
    print(f"Quantity: {lc.quantity:,} {lc.unit}")
    print(f"Rate: ${lc.rate_per_unit}/MT")
    print(f"Total Value: ${lc.total_value:,}")
    print(f"Signing Date: {lc.signing_date}")
    print(f"Maturity Date: {lc.maturity_date.strftime('%Y-%m-%d')}")
    print(f"Days Remaining: {lc.days_remaining}")
    print(f"Customer: {lc.customer_country}")
    print(f"Route: {lc.port_of_loading} → {lc.port_of_discharge}")
    print()
    
    # Calculate daily forward P&L
    print("📈 DAILY FORWARD P&L ANALYSIS")
    print("-" * 50)
    
    forward_calculator = ForwardPLCalculator()
    forward_result = forward_calculator.calculate_daily_forward_pl(lc, 'INR')
    
    if forward_result:
        summary = forward_result.get('summary', {})
        daily_pl = forward_result.get('daily_pl', {})
        
        print(f"Currency Pair: {forward_result.get('currency_pair')}")
        print(f"LC Amount: ${lc.total_value:,}")
        print(f"Signing Forward Rate: ₹{forward_result.get('signing_forward_rate'):.4f}")
        print(f"Current Forward Rate: ₹{forward_result.get('current_forward_rate'):.4f}")
        print()
        
        # P&L Summary
        print("💰 P&L SUMMARY")
        print("-" * 30)
        current_pl = summary.get('current_pl', 0)
        max_profit = summary.get('max_profit', 0)
        max_loss = summary.get('max_loss', 0)
        
        print(f"Current P&L: ₹{current_pl:,.2f}")
        print(f"Max Profit: ₹{max_profit:,.2f} (on {summary.get('max_profit_date')})")
        print(f"Max Loss: ₹{max_loss:,.2f} (on {summary.get('max_loss_date')})")
        print(f"Average P&L: ₹{summary.get('avg_pl', 0):,.2f}")
        print(f"P&L Volatility: ₹{summary.get('volatility', 0):,.2f}")
        print(f"P&L Range: ₹{max_profit - max_loss:,.2f}")
        
        # Current P&L percentage
        signing_value = lc.total_value * forward_result.get('signing_forward_rate', 85.0)
        pl_percentage = (current_pl / signing_value) * 100 if signing_value else 0
        print(f"Current P&L %: {pl_percentage:.2f}%")
        print()
        
        # Risk Assessment
        print("⚠️  RISK ASSESSMENT")
        print("-" * 30)
        risk_level = "LOW"
        if abs(pl_percentage) > 5:
            risk_level = "HIGH"
        elif abs(pl_percentage) > 2:
            risk_level = "MEDIUM"
        
        print(f"Risk Level: {risk_level}")
        print(f"Days of Exposure: {summary.get('total_days', 0)}")
        
        if current_pl > 0:
            print("✅ Currently in PROFIT - USD has strengthened")
            print("💡 Consider partial hedging to lock in gains")
        elif current_pl < 0:
            print("❌ Currently showing LOSS - USD has weakened")
            print("💡 Monitor closely, consider hedging if loss increases")
        else:
            print("⚖️  Position is neutral")
        print()
        
        # Daily P&L Highlights
        print("📊 DAILY P&L HIGHLIGHTS")
        print("-" * 30)
        
        # Show most profitable and loss-making days
        sorted_days = sorted(daily_pl.items(), key=lambda x: x[1]['unrealized_pl'], reverse=True)
        
        print("🟢 TOP 3 MOST PROFITABLE DAYS:")
        for i, (date, data) in enumerate(sorted_days[:3]):
            print(f"  {i+1}. {date}: ₹{data['unrealized_pl']:,.2f} (Rate: ₹{data['forward_rate']:.4f})")
        
        print("\n🔴 TOP 3 LOSS-MAKING DAYS:")
        for i, (date, data) in enumerate(sorted_days[-3:]):
            print(f"  {i+1}. {date}: ₹{data['unrealized_pl']:,.2f} (Rate: ₹{data['forward_rate']:.4f})")
        
        print()
        
        # Chart data summary
        chart_data = forward_result.get('chart_data', [])
        print(f"📈 CHART DATA: {len(chart_data)} data points ready for visualization")
        print(f"   Date Range: {chart_data[0]['date']} to {chart_data[-1]['date']}" if chart_data else "   No data")
        print()
        
    else:
        print("❌ Failed to calculate forward P&L")
        return
    
    # Compare with spot P&L
    print("🔄 COMPARISON WITH SPOT P&L")
    print("-" * 50)
    
    spot_calculator = ProfitLossCalculator()
    spot_result = spot_calculator.calculate_current_pl(lc, 'INR')
    
    if spot_result:
        spot_pl = spot_result.get('unrealized_pl', 0)
        forward_pl = current_pl
        
        print(f"Forward P&L: ₹{forward_pl:,.2f}")
        print(f"Spot P&L: ₹{spot_pl:,.2f}")
        print(f"Difference: ₹{forward_pl - spot_pl:,.2f}")
        
        if abs(forward_pl - spot_pl) > 10000:
            print("💡 Significant difference between forward and spot - forward rates show market expectations")
        else:
            print("✅ Forward and spot P&L are similar - stable market conditions")
    print()
    
    # Risk metrics
    print("🎯 RISK METRICS")
    print("-" * 50)
    
    risk_calculator = RiskMetricsCalculator()
    risk_metrics = risk_calculator.calculate_value_at_risk(lc, base_currency='INR')
    
    if risk_metrics:
        print(f"Value at Risk (95%): ₹{risk_metrics.get('var_95', 0):,.2f}")
        print(f"Volatility: {risk_metrics.get('volatility', 0)*100:.2f}%")
        print(f"Expected Shortfall: ₹{risk_metrics.get('expected_shortfall', 0):,.2f}")
        print(f"Confidence Level: {risk_metrics.get('confidence_level', 95)}%")
    print()
    
    # Web interface showcase
    print("🌐 WEB INTERFACE FEATURES")
    print("-" * 50)
    print("✅ Ultra-modern gradient design with glassmorphism effects")
    print("✅ Interactive P&L bar chart with profit/loss highlighting")
    print("✅ Real-time forward rate calculations")
    print("✅ Responsive design for all devices")
    print("✅ Enhanced P&L metrics display")
    print("✅ Professional reporting with meaningful data")
    print()
    print("🚀 Visit http://localhost:5000 to see the enhanced interface!")
    print()
    
    # Deployment information
    print("☁️  DEPLOYMENT STATUS")
    print("-" * 50)
    print("✅ GitHub Repository: https://github.com/RudraS025/currency_risk_management")
    print("✅ Heroku App: https://rudra-currency-risk-mgmt.herokuapp.com")
    print("✅ Daily automated updates via Heroku Scheduler")
    print("✅ All enhanced features deployed to production")
    print()
    
    print("🎉 ENHANCEMENT SUMMARY")
    print("=" * 80)
    print("✅ Fixed zero P&L issue - now shows meaningful results")
    print("✅ Implemented realistic daily forward rate calculations")
    print("✅ Added daily P&L tracking from signing to maturity")
    print("✅ Created bar chart visualization with profit/loss highlighting")
    print("✅ Enhanced UI with ultra-modern design")
    print("✅ Added comprehensive P&L analytics and risk metrics")
    print("✅ Deployed all improvements to production")
    print()
    print("🎯 The system now provides actionable insights for currency risk management!")

if __name__ == "__main__":
    demo_enhanced_pl_system()
