"""
Example usage of the Currency Risk Management System.

This script demonstrates how to use the system with the example scenario:
- Client sells 1000 tons of paddy to Iran
- Rate: USD 400/ton
- LC signed: 16.06.2025
- Duration: 90 days
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currency_risk_mgmt import (
    LetterOfCredit, 
    ForexDataProvider, 
    ProfitLossCalculator,
    RiskMetricsCalculator,
    ReportGenerator
)
from currency_risk_mgmt.reports.visualizations import VisualizationEngine


def main():
    """Main example function."""
    print("Currency Risk Management System - Example Usage")
    print("=" * 60)
    
    # Create the Letter of Credit for your scenario
    print("\n1. Creating Letter of Credit...")
    
    lc = LetterOfCredit(
        lc_id="LC001_PADDY_IRAN",
        commodity="Paddy",
        quantity=1000,
        unit="tons",
        rate_per_unit=400,
        currency="USD",
        signing_date="2025-06-16",
        maturity_days=90,
        customer_country="Iran",
        incoterm="FOB",
        description="Paddy export to Iran - 1000 tons at USD 400/ton"
    )
    
    print(f"Created LC: {lc}")
    print(f"Total Value: {lc.currency} {lc.total_value:,.2f}")
    print(f"Maturity Date: {lc.maturity_date.strftime('%Y-%m-%d')}")
    print(f"Days Remaining: {lc.days_remaining}")
    
    # Initialize data provider and calculators
    print("\n2. Initializing Data Providers...")
    
    forex_provider = ForexDataProvider()
    pl_calculator = ProfitLossCalculator(forex_provider)
    risk_calculator = RiskMetricsCalculator(forex_provider)
    report_generator = ReportGenerator(forex_provider)
    viz_engine = VisualizationEngine(forex_provider)
    
    # Check data source health
    print("\n3. Checking Data Source Health...")
    health = forex_provider.health_check()
    for source, status in health.items():
        status_text = "✓ Healthy" if status else "✗ Unavailable"
        print(f"   {source}: {status_text}")
    
    # Get current exchange rate
    print("\n4. Current Exchange Rate...")
    current_rate = forex_provider.get_current_rate("USD", "INR")
    if current_rate:
        print(f"   USD/INR Rate: {current_rate:.4f}")
        
        # Get rate with confidence
        rate, confidence = forex_provider.get_rate_with_confidence("USD", "INR")
        print(f"   Confidence Score: {confidence}%")
    else:
        print("   Unable to fetch current rate")
        return
    
    # Calculate current P&L
    print("\n5. Current Profit & Loss Analysis...")
    current_pl = pl_calculator.calculate_current_pl(lc)
    
    if current_pl.get('unrealized_pl') is not None:
        print(f"   LC Value at Signing: ₹{current_pl['lc_value_base_at_signing']:,.2f}")
        print(f"   LC Value Current: ₹{current_pl['lc_value_base_current']:,.2f}")
        print(f"   Unrealized P&L: ₹{current_pl['unrealized_pl']:,.2f}")
        print(f"   P&L Percentage: {current_pl['pl_percentage']:.2f}%")
        print(f"   Daily P&L: ₹{current_pl['daily_pl']:,.2f}")
        
        if current_pl['unrealized_pl'] > 0:
            print("   Status: 📈 PROFIT")
        else:
            print("   Status: 📉 LOSS")
    else:
        print("   Unable to calculate P&L")
        return
    
    # Forward rate projection
    print("\n6. Forward Rate Projection...")
    forward_pl = pl_calculator.calculate_forward_pl_projection(lc)
    
    if forward_pl.get('projected_pl') is not None:
        print(f"   Forward Rate Estimate: {forward_pl['forward_rate']:.4f}")
        print(f"   Projected P&L at Maturity: ₹{forward_pl['projected_pl']:,.2f}")
        print(f"   Projected P&L Percentage: {forward_pl['projected_pl_percentage']:.2f}%")
    
    # Risk Analysis
    print("\n7. Risk Analysis...")
    var_analysis = risk_calculator.calculate_value_at_risk(lc)
    
    if var_analysis.get('var_absolute'):
        print(f"   Value at Risk (95%): ₹{var_analysis['var_absolute']:,.2f}")
        print(f"   VaR Percentage: {var_analysis['var_percentage']:.2f}%")
        print(f"   Daily Volatility: {var_analysis['daily_volatility']:.4f}")
        
        # Risk level assessment
        var_pct = var_analysis['var_percentage']
        if var_pct < 5:
            risk_level = "🟢 LOW RISK"
        elif var_pct < 15:
            risk_level = "🟡 MEDIUM RISK"
        else:
            risk_level = "🔴 HIGH RISK"
        
        print(f"   Risk Level: {risk_level}")
    
    # Expected Shortfall
    expected_shortfall = risk_calculator.calculate_expected_shortfall(lc)
    if expected_shortfall.get('expected_shortfall_absolute'):
        print(f"   Expected Shortfall: ₹{expected_shortfall['expected_shortfall_absolute']:,.2f}")
    
    # Scenario Analysis
    print("\n8. Scenario Analysis...")
    current_rate = current_pl.get('current_rate', 0)
    if current_rate > 0:
        scenarios = [
            current_rate * 0.85,  # -15%
            current_rate * 0.90,  # -10%
            current_rate * 0.95,  # -5%
            current_rate,         # Current
            current_rate * 1.05,  # +5%
            current_rate * 1.10,  # +10%
            current_rate * 1.15   # +15%
        ]
        
        scenario_results = pl_calculator.calculate_scenario_analysis(lc, scenarios)
        
        print("   Rate Change | Exchange Rate | P&L Impact")
        print("   " + "-" * 45)
        
        for result in scenario_results:
            rate_change = result['rate_change_percentage']
            scenario_rate = result['scenario_rate']
            scenario_pl = result['scenario_pl']
            
            if rate_change == 0:
                marker = " (Current)"
            elif scenario_pl > 0:
                marker = " 📈"
            else:
                marker = " 📉"
            
            print(f"   {rate_change:+6.1f}%    | {scenario_rate:8.4f}    | ₹{scenario_pl:10,.0f}{marker}")
    
    # Generate comprehensive report
    print("\n9. Generating Comprehensive Report...")
    
    try:
        report = report_generator.generate_lc_summary_report(lc)
        
        if report.get('lc_information'):
            print(f"   Report ID: {report['report_id']}")
            print(f"   Generated: {report['generation_timestamp']}")
            
            # Save reports
            json_file = report_generator.save_report_json(report, "paddy_export_report")
            if json_file:
                print(f"   JSON Report saved: {json_file}")
            
            excel_file = report_generator.export_report_to_excel(report, "paddy_export_report.xlsx")
            if excel_file:
                print(f"   Excel Report saved: {excel_file}")
            
            # Show recommendations
            recommendations = report.get('recommendations', [])
            if recommendations:
                print("\n10. Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"    {i}. {rec}")
        
    except Exception as e:
        print(f"   Error generating report: {e}")
    
    # Show break-even analysis
    print("\n11. Break-even Analysis...")
    break_even_rate = pl_calculator.calculate_break_even_rate(lc)
    if break_even_rate:
        current_rate = current_pl.get('current_rate', 0)
        if current_rate > 0:
            rate_diff_pct = ((current_rate - break_even_rate) / break_even_rate) * 100
            print(f"   Break-even Rate: {break_even_rate:.4f}")
            print(f"   Current Rate: {current_rate:.4f}")
            print(f"   Rate Difference: {rate_diff_pct:+.2f}%")
            
            if rate_diff_pct > 0:
                print("   Status: 💰 Above break-even (Profitable)")
            else:
                print("   Status: ⚠️ Below break-even (Loss)")
    
    # Show summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"LC ID: {lc.lc_id}")
    print(f"Commodity: {lc.commodity} ({lc.quantity:,.0f} {lc.unit})")
    print(f"Total Value: {lc.currency} {lc.total_value:,.2f}")
    print(f"Current P&L: ₹{current_pl.get('unrealized_pl', 0):,.2f} ({current_pl.get('pl_percentage', 0):.2f}%)")
    print(f"Days to Maturity: {lc.days_remaining}")
    print(f"Risk Level: {risk_level if 'risk_level' in locals() else 'Unknown'}")
    
    print("\n📊 Reports generated successfully!")
    print("📈 Use the Excel file for detailed analysis and charts")
    print("🔄 Run this script regularly to monitor your position")
    
    return report if 'report' in locals() else None


if __name__ == "__main__":
    # Set up logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        result = main()
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
