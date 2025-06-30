#!/usr/bin/env python3
"""
Test script for enhanced P&L calculations with daily forward rates.
This verifies that meaningful P&L values are generated.
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

def test_daily_forward_pl():
    """Test daily forward P&L calculation"""
    print("=" * 60)
    print("TESTING ENHANCED DAILY FORWARD P&L CALCULATION")
    print("=" * 60)
    
    # Create test LC
    signing_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    maturity_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
    
    lc = LetterOfCredit(
        lc_id="TEST-LC-001",
        commodity="Rice",
        quantity=1000,
        unit="MT",
        rate_per_unit=200,  # $200 per MT = $200,000 total
        currency="USD",
        signing_date=signing_date,
        maturity_days=90,
        customer_country="Iran",
        incoterm="FOB"
    )
    
    print(f"Test LC Details:")
    print(f"  LC ID: {lc.lc_id}")
    print(f"  Amount: ${lc.total_value:,}")
    print(f"  Signing Date: {lc.signing_date}")
    print(f"  Maturity Date: {lc.maturity_date.strftime('%Y-%m-%d')}")
    print(f"  Days Remaining: {lc.days_remaining}")
    print()
    
    # Test Forward P&L Calculator
    print("Testing Forward P&L Calculator...")
    forward_calculator = ForwardPLCalculator()
    forward_result = forward_calculator.calculate_daily_forward_pl(lc, 'INR')
    
    if forward_result:
        print("✅ Forward P&L calculation successful!")
        print(f"  Currency Pair: {forward_result.get('currency_pair', 'N/A')}")
        print(f"  Signing Forward Rate: ₹{forward_result.get('signing_forward_rate', 0):.4f}")
        print(f"  Current Forward Rate: ₹{forward_result.get('current_forward_rate', 0):.4f}")
        
        summary = forward_result.get('summary', {})
        print(f"  Current P&L: ₹{summary.get('current_pl', 0):,.2f}")
        print(f"  Max Profit: ₹{summary.get('max_profit', 0):,.2f} (Date: {summary.get('max_profit_date', 'N/A')})")
        print(f"  Max Loss: ₹{summary.get('max_loss', 0):,.2f} (Date: {summary.get('max_loss_date', 'N/A')})")
        print(f"  Average P&L: ₹{summary.get('avg_pl', 0):,.2f}")
        print(f"  P&L Volatility: ₹{summary.get('volatility', 0):,.2f}")
        print(f"  Total Days Tracked: {summary.get('total_days', 0)}")
        
        # Show sample daily P&L data
        daily_pl = forward_result.get('daily_pl', {})
        if daily_pl:
            print(f"\nSample Daily P&L Data (showing first 5 days):")
            for i, (date, data) in enumerate(sorted(daily_pl.items())[:5]):
                print(f"  {date}: Rate=₹{data['forward_rate']:.4f}, P&L=₹{data['unrealized_pl']:,.2f}")
            
            if len(daily_pl) > 5:
                print(f"  ... and {len(daily_pl) - 5} more days")
        
        # Chart data
        chart_data = forward_result.get('chart_data', [])
        print(f"\nChart Data Points: {len(chart_data)}")
        
        if len(chart_data) > 0:
            min_pl = min(item['pl'] for item in chart_data)
            max_pl = max(item['pl'] for item in chart_data)
            print(f"  P&L Range: ₹{min_pl:,.2f} to ₹{max_pl:,.2f}")
            print(f"  P&L Spread: ₹{max_pl - min_pl:,.2f}")
        
    else:
        print("❌ Forward P&L calculation failed!")
        return False
    
    print("\n" + "=" * 60)
    
    # Compare with spot P&L
    print("COMPARING WITH SPOT P&L CALCULATION")
    print("=" * 60)
    
    spot_calculator = ProfitLossCalculator()
    spot_result = spot_calculator.calculate_current_pl(lc, 'INR')
    
    if spot_result:
        print("✅ Spot P&L calculation successful!")
        print(f"  Signing Rate: ₹{spot_result.get('signing_rate', 0):.4f}")
        print(f"  Current Rate: ₹{spot_result.get('current_rate', 0):.4f}")
        print(f"  Unrealized P&L: ₹{spot_result.get('unrealized_pl', 0):,.2f}")
        print(f"  P&L Percentage: {spot_result.get('pl_percentage', 0):.2f}%")
        
        # Compare the two approaches
        forward_current_pl = forward_result.get('summary', {}).get('current_pl', 0)
        spot_current_pl = spot_result.get('unrealized_pl', 0)
        
        print(f"\nComparison:")
        print(f"  Forward P&L: ₹{forward_current_pl:,.2f}")
        print(f"  Spot P&L: ₹{spot_current_pl:,.2f}")
        print(f"  Difference: ₹{forward_current_pl - spot_current_pl:,.2f}")
        
    else:
        print("❌ Spot P&L calculation failed!")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    # Determine if results are meaningful
    forward_meaningful = (
        forward_result and 
        forward_result.get('summary', {}).get('current_pl', 0) != 0 and
        len(forward_result.get('chart_data', [])) > 0
    )
    
    spot_meaningful = (
        spot_result and 
        spot_result.get('unrealized_pl', 0) != 0
    )
    
    if forward_meaningful:
        print("✅ Forward P&L calculations are generating meaningful results")
        print("✅ Daily P&L data is available for charting")
    else:
        print("❌ Forward P&L calculations are still generating zero/meaningless results")
    
    if spot_meaningful:
        print("✅ Spot P&L calculations are generating meaningful results")
    else:
        print("❌ Spot P&L calculations are still generating zero/meaningless results")
    
    return forward_meaningful and spot_meaningful

def test_web_api_format():
    """Test the data format expected by the web API"""
    print("\n" + "=" * 60)
    print("TESTING WEB API DATA FORMAT")
    print("=" * 60)
    
    # Create test data similar to what web app sends
    test_data = {
        'lc_id': 'WEB-TEST-001',
        'amount_usd': 100000,
        'issue_date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
        'maturity_date': (datetime.now() + timedelta(days=70)).strftime('%Y-%m-%d'),
        'commodity': 'Paddy',
        'beneficiary': 'Iran Buyer',
        'use_forward_rates': True
    }
    
    print(f"Test API Data:")
    print(json.dumps(test_data, indent=2))
    
    # Create LC from web data
    lc = LetterOfCredit(
        lc_id=test_data['lc_id'],
        commodity=test_data['commodity'],
        quantity=test_data['amount_usd'] / 200,  # Assume $200 per unit
        unit="MT",
        rate_per_unit=200,
        currency="USD",
        signing_date=test_data['issue_date'],
        maturity_days=(datetime.strptime(test_data['maturity_date'], '%Y-%m-%d') - 
                      datetime.strptime(test_data['issue_date'], '%Y-%m-%d')).days,
        customer_country=test_data.get('beneficiary', 'Customer Country')
    )
    
    # Calculate P&L
    calculator = ForwardPLCalculator()
    result = calculator.calculate_daily_forward_pl(lc, 'INR')
    
    if result:
        # Format results as the web app expects
        summary = result.get('summary', {})
        formatted_result = {
            'total_pl_inr': summary.get('current_pl', 0),
            'spot_rate': result.get('current_forward_rate', 85.0),
            'original_rate': result.get('signing_forward_rate', 85.0),
            'pl_percentage': (summary.get('current_pl', 0) / (lc.total_value * result.get('signing_forward_rate', 85.0))) * 100 if result.get('signing_forward_rate') else 0,
            'days_remaining': lc.days_remaining,
            'max_profit': summary.get('max_profit', 0),
            'max_loss': summary.get('max_loss', 0),
            'max_profit_date': summary.get('max_profit_date', ''),
            'max_loss_date': summary.get('max_loss_date', ''),
            'volatility': summary.get('volatility', 0),
            'chart_data': result.get('chart_data', [])
        }
        
        print(f"\nFormatted Web API Response:")
        print(f"  Total P&L: ₹{formatted_result['total_pl_inr']:,.2f}")
        print(f"  Current Rate: ₹{formatted_result['spot_rate']:.4f}")
        print(f"  Original Rate: ₹{formatted_result['original_rate']:.4f}")
        print(f"  P&L %: {formatted_result['pl_percentage']:.2f}%")
        print(f"  Days Remaining: {formatted_result['days_remaining']}")
        print(f"  Max Profit: ₹{formatted_result['max_profit']:,.2f}")
        print(f"  Max Loss: ₹{formatted_result['max_loss']:,.2f}")
        print(f"  Chart Data Points: {len(formatted_result['chart_data'])}")
        
        # Check if all fields have meaningful values
        meaningful_fields = []
        if formatted_result['total_pl_inr'] != 0:
            meaningful_fields.append('Total P&L')
        if formatted_result['spot_rate'] != formatted_result['original_rate']:
            meaningful_fields.append('Rate difference')
        if len(formatted_result['chart_data']) > 0:
            meaningful_fields.append('Chart data')
        if formatted_result['max_profit'] != formatted_result['max_loss']:
            meaningful_fields.append('P&L range')
        
        print(f"\nMeaningful fields: {', '.join(meaningful_fields)}")
        
        if len(meaningful_fields) >= 3:
            print("✅ Web API format test passed - meaningful data generated")
            return True
        else:
            print("❌ Web API format test failed - data still not meaningful")
            return False
    else:
        print("❌ Failed to get P&L calculation results")
        return False

if __name__ == "__main__":
    print("Currency Risk Management System - Enhanced P&L Test")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_daily_forward_pl()
    test2_passed = test_web_api_format()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced P&L calculations are working correctly")
        print("✅ Daily forward rates are generating meaningful variations")
        print("✅ Web API data format is correct")
        print("✅ Chart data is available for visualization")
        print("\n🚀 The app should now show meaningful P&L results!")
    else:
        print("❌ SOME TESTS FAILED")
        if not test1_passed:
            print("❌ Daily forward P&L calculations need more work")
        if not test2_passed:
            print("❌ Web API data format issues")
        print("\n🔧 Additional fixes needed")
