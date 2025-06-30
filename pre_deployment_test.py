"""
Pre-deployment System Test
Tests all major components before deployment
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_system():
    """Test all core system components"""
    print("🧪 Testing Currency Risk Management System")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
        from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
        from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
        from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
        from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
        from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator
        from currency_risk_mgmt.reports.generator import ReportGenerator
        from currency_risk_mgmt.reports.forward_reports import ForwardRatesReportGenerator
        print("✅ All imports successful")
        
        # Test LC creation
        print("\n📄 Testing Letter of Credit...")
        lc = LetterOfCredit(
            lc_id="TEST-LC-001",
            commodity="Test Export",
            quantity=1000,
            unit="tons",
            rate_per_unit=100,
            currency="USD",
            signing_date="2025-01-01",
            maturity_days=90,
            customer_country="Iran"
        )
        print(f"✅ LC created: {lc.lc_id}, Amount: ${lc.quantity * lc.rate_per_unit:,}")
        
        # Test forex provider
        print("\n💱 Testing forex data...")
        forex_provider = ForexDataProvider()
        current_rate = forex_provider.get_current_rate('USD', 'INR')
        print(f"✅ Current USD/INR rate: {current_rate}")
        
        # Test forward rates
        print("\n📈 Testing forward rates...")
        forward_provider = ForwardRatesProvider()
        forward_curve = forward_provider.get_forward_curve('USD', 'INR', datetime.now().strftime('%Y-%m-%d'))
        forward_rate = forward_curve.get('90d', 85.0)  # Get 90-day rate or default
        print(f"✅ Forward rates curve available: {len(forward_curve)} periods")
        
        # Test P&L calculation
        print("\n💰 Testing P&L calculation...")
        pl_calculator = ProfitLossCalculator()
        pl_result = pl_calculator.calculate_current_pl(lc, 'INR')
        print(f"✅ P&L calculated: ₹{pl_result.get('unrealized_pl', 0):,.2f}")
        
        # Test forward P&L
        print("\n📊 Testing forward P&L...")
        forward_calculator = ForwardPLCalculator()
        forward_pl = forward_calculator.calculate_daily_forward_pl(lc, 'INR')
        print(f"✅ Forward P&L: ₹{forward_pl.get('daily_pl', {}).get('today', 0):,.2f}")
        
        # Test risk metrics
        print("\n⚠️ Testing risk metrics...")
        risk_calculator = RiskMetricsCalculator()
        risk_metrics = risk_calculator.calculate_value_at_risk(lc, base_currency='INR')
        print(f"✅ Risk metrics calculated: VaR 95%: ₹{risk_metrics.get('var_95', 0):,.2f}")
        
        # Test report generation
        print("\n📋 Testing report generation...")
        report_gen = ReportGenerator()
        report = report_gen.generate_lc_summary_report(lc, 'INR')
        print(f"✅ Report generated with {len(report)} sections")
        
        # Test forward reports
        print("\n📈 Testing forward reports...")
        forward_report_gen = ForwardRatesReportGenerator()
        forward_report = forward_report_gen.generate_comprehensive_report(lc, 'INR')
        print(f"✅ Forward report generated")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
        print("🚀 You can now deploy to GitHub and Heroku")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app():
    """Test Flask web application imports"""
    print("\n🌐 Testing web application...")
    try:
        # Test Flask app creation
        import app
        print("✅ Flask app imports successfully")
        print("✅ Web dashboard ready for deployment")
        return True
    except Exception as e:
        print(f"❌ Web app test failed: {str(e)}")
        return False

def test_scheduler():
    """Test daily scheduler"""
    print("\n⏰ Testing daily scheduler...")
    try:
        from examples.daily_update_scheduler import DailyUpdateScheduler
        scheduler = DailyUpdateScheduler()
        print("✅ Daily scheduler ready")
        return True
    except Exception as e:
        print(f"❌ Scheduler test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏁 PRE-DEPLOYMENT SYSTEM TEST")
    print("Testing all components before GitHub/Heroku deployment")
    print("=" * 60)
    
    # Run all tests
    core_test = test_core_system()
    web_test = test_web_app()
    scheduler_test = test_scheduler()
    
    print("\n" + "=" * 60)
    if all([core_test, web_test, scheduler_test]):
        print("🎊 SYSTEM IS READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("1. Run: git add . && git commit -m 'Deploy: Complete system'")
        print("2. Run: git push origin main")
        print("3. Deploy to Heroku using commands in HEROKU_DEPLOYMENT.md")
    else:
        print("❌ SYSTEM NOT READY - Please fix errors above")
    print("=" * 60)
