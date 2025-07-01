"""
Simple test to check why the real 2025 data isn't being used in the web API.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025

def test_real_data_availability():
    """Test if real data availability check is working."""
    
    print("Testing Real Data Availability Check...")
    
    calculator = RealForwardPLCalculator2025()
    
    # Test with the exact dates from the web API
    issue_date = "2025-06-16"
    maturity_date = "2025-09-16"
    
    print(f"Issue Date: {issue_date}")
    print(f"Maturity Date: {maturity_date}")
    
    # Check availability
    is_available = calculator.is_real_data_available(issue_date, maturity_date)
    print(f"Real Data Available: {is_available}")
    
    # Get data coverage
    data_summary = calculator.get_data_summary()
    print(f"Data Summary: {data_summary}")
    
    # Test the provider directly
    from currency_risk_mgmt.data_providers.real_forward_rates_2025 import RealForwardRatesProvider2025
    provider = RealForwardRatesProvider2025()
    
    coverage = provider.get_data_coverage()
    print(f"Provider Coverage: {coverage}")
    
    # Test if we can get rates for the specific dates
    rate_16_june = provider.get_forward_rate("2025-06-16", "2025-09-16")
    print(f"Rate for June 16, 2025: {rate_16_june}")
    
    rate_16_sep = provider.get_forward_rate("2025-09-16", "2025-09-16")
    print(f"Rate for Sep 16, 2025: {rate_16_sep}")
    
    # Test the availability function
    print(f"Provider availability check: {provider.is_data_available(issue_date, maturity_date)}")
    
    return is_available

if __name__ == "__main__":
    test_real_data_availability()
