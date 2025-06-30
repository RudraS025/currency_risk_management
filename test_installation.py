"""
Quick test script to verify the Currency Risk Management System installation.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")
    
    try:
        from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
        print("✅ LetterOfCredit import successful")
    except ImportError as e:
        print(f"❌ LetterOfCredit import failed: {e}")
        return False
    
    try:
        from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
        print("✅ ForexDataProvider import successful")
    except ImportError as e:
        print(f"❌ ForexDataProvider import failed: {e}")
        return False
    
    try:
        from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
        print("✅ ProfitLossCalculator import successful")
    except ImportError as e:
        print(f"❌ ProfitLossCalculator import failed: {e}")
        return False
    
    try:
        from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator
        print("✅ RiskMetricsCalculator import successful")
    except ImportError as e:
        print(f"❌ RiskMetricsCalculator import failed: {e}")
        return False
    
    try:
        from currency_risk_mgmt.reports.generator import ReportGenerator
        print("✅ ReportGenerator import successful")
    except ImportError as e:
        print(f"❌ ReportGenerator import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
        
        # Create a test LC
        lc = LetterOfCredit(
            lc_id="TEST001",
            commodity="Test Commodity",
            quantity=100,
            unit="tons",
            rate_per_unit=500,
            currency="USD",
            signing_date="2025-06-16",
            maturity_days=90,
            customer_country="Test Country"
        )
        
        print(f"✅ Created test LC: {lc.lc_id}")
        print(f"   Total Value: {lc.currency} {lc.total_value:,.2f}")
        print(f"   Days Remaining: {lc.days_remaining}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_forex_provider():
    """Test forex data provider."""
    print("\nTesting forex data provider...")
    
    try:
        from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
        
        provider = ForexDataProvider()
        health = provider.health_check()
        
        print("📊 Data source health check:")
        for source, status in health.items():
            status_text = "✅ Healthy" if status else "⚠️ Unavailable"
            print(f"   {source}: {status_text}")
        
        # Try to get a rate
        rate = provider.get_current_rate("USD", "INR")
        if rate:
            print(f"✅ Retrieved USD/INR rate: {rate:.4f}")
        else:
            print("⚠️ Could not retrieve current rate (this is normal if APIs are rate-limited)")
        
        return True
        
    except Exception as e:
        print(f"❌ Forex provider test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Currency Risk Management System - Installation Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    # Test forex provider
    if not test_forex_provider():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python examples/demo_paddy_export.py' for a complete demo")
        print("2. Check the generated Excel and JSON reports")
        print("3. Modify the demo script for your specific use case")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
