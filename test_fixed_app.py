#!/usr/bin/env python3
"""
Quick test to verify the fixed app produces meaningful P&L results
"""

import requests
import json
from datetime import datetime, timedelta

def test_fixed_app():
    print("🧪 TESTING FIXED CURRENCY RISK MANAGEMENT APP")
    print("=" * 60)
    
    # Test data - same as what user would enter
    test_data = {
        'lc_number': 'TEST-FIX-001',
        'amount_usd': 150000,  # $150,000
        'issue_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'maturity_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
        'commodity': 'Rice Export',
        'beneficiary': 'Iran Customer',
        'use_forward_rates': True
    }
    
    print(f"Test Data:")
    print(f"  LC Amount: ${test_data['amount_usd']:,}")
    print(f"  Issue Date: {test_data['issue_date']}")
    print(f"  Maturity Date: {test_data['maturity_date']}")
    print(f"  Forward Rates: {test_data['use_forward_rates']}")
    print()
    
    try:
        # Test P&L Calculation
        print("🧮 Testing P&L Calculation...")
        response = requests.post('http://localhost:5000/api/calculate-pl', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pl_result = data.get('pl_result', {})
                print("✅ P&L Calculation SUCCESS!")
                print(f"  Total P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"  Current Rate: ₹{pl_result.get('spot_rate', 0):.4f}")
                print(f"  Original Rate: ₹{pl_result.get('original_rate', 0):.4f}")
                print(f"  P&L %: {pl_result.get('pl_percentage', 0):.2f}%")
                print(f"  Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"  Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"  Chart Data Points: {len(pl_result.get('chart_data', []))}")
                
                # Check if results are meaningful
                is_meaningful = (
                    pl_result.get('total_pl_inr', 0) != 0 or
                    pl_result.get('spot_rate', 0) != pl_result.get('original_rate', 0) or
                    len(pl_result.get('chart_data', [])) > 0
                )
                
                if is_meaningful:
                    print("🎉 RESULTS ARE MEANINGFUL!")
                else:
                    print("❌ Results are still not meaningful")
                    
            else:
                print(f"❌ P&L Calculation failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print()
    
    try:
        # Test Scenario Analysis
        print("📊 Testing Scenario Analysis...")
        response = requests.post('http://localhost:5000/api/scenario-analysis', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scenarios = data.get('scenarios', [])
                print("✅ Scenario Analysis SUCCESS!")
                for scenario in scenarios:
                    print(f"  {scenario.get('scenario_name', 'Unknown')}: "
                          f"₹{scenario.get('pl_inr', 0):,.2f} "
                          f"({scenario.get('rate_change_percent', 0):+.1f}%)")
                
                # Check if scenarios are meaningful
                scenario_meaningful = any(s.get('pl_inr', 0) != 0 for s in scenarios)
                if scenario_meaningful:
                    print("🎉 SCENARIO RESULTS ARE MEANINGFUL!")
                else:
                    print("❌ Scenario results are still not meaningful")
                    
            else:
                print(f"❌ Scenario Analysis failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Scenario test failed: {e}")
    
    print()
    
    try:
        # Test Report Generation
        print("📋 Testing Report Generation...")
        response = requests.post('http://localhost:5000/api/generate-report', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report = data.get('report', {})
                print("✅ Report Generation SUCCESS!")
                
                pl_analysis = report.get('pl_analysis', {})
                if pl_analysis:
                    print(f"  Current P&L: ₹{pl_analysis.get('current_pl', 0):,.2f}")
                    print(f"  Max Profit: ₹{pl_analysis.get('max_profit', 0):,.2f}")
                    print(f"  Days Analyzed: {pl_analysis.get('total_days_analyzed', 0)}")
                    
                    # Check if report has meaningful data
                    report_meaningful = (
                        pl_analysis.get('current_pl', 0) != 0 or
                        pl_analysis.get('total_days_analyzed', 0) > 0
                    )
                    
                    if report_meaningful:
                        print("🎉 REPORT HAS MEANINGFUL DATA!")
                    else:
                        print("❌ Report still lacks meaningful data")
                else:
                    print("⚠️ Report structure changed, but generated successfully")
                    
            else:
                print(f"❌ Report Generation failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Report test failed: {e}")

    print()
    print("🎯 TESTING COMPLETE!")
    print("If all tests show 'MEANINGFUL' results, the app is fixed!")

if __name__ == "__main__":
    test_fixed_app()
