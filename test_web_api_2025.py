"""
Test the web API with real 2025 LC data to verify it produces meaningful results.
"""

import requests
import json
from datetime import datetime

def test_web_api_2025():
    """Test the web API with real 2025 LC data."""
    
    print("="*80)
    print("TESTING WEB API WITH REAL 2025 LC DATA")
    print("="*80)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test data - Real 2025 LC from user's spreadsheet
    lc_data = {
        "lc_number": "REAL-2025-SONA-MASURI",
        "commodity": "SONA MASURI Rice Export",
        "amount_usd": 400000,  # $400,000 as per spreadsheet
        "issue_date": "2025-06-16",  # Real LC issue date
        "maturity_date": "2025-09-16",  # Real LC maturity date (Sep 16, 2025)
        "beneficiary": "GTC IRAN"
    }
    
    print(f"Testing with Real LC Data:")
    print(f"  LC Number: {lc_data['lc_number']}")
    print(f"  Commodity: {lc_data['commodity']}")
    print(f"  Amount: ${lc_data['amount_usd']:,}")
    print(f"  Issue Date: {lc_data['issue_date']}")
    print(f"  Maturity Date: {lc_data['maturity_date']}")
    print(f"  Beneficiary: {lc_data['beneficiary']}")
    
    # Test 1: Current Rates API
    print("\n1. Testing Current Rates API...")
    try:
        response = requests.get(f"{base_url}/api/current-rates", timeout=10)
        if response.status_code == 200:
            rates_data = response.json()
            print(f"   ✓ Current USD/INR Rate: {rates_data.get('rate', 'N/A')}")
            print(f"   ✓ Source: {rates_data.get('source', 'N/A')}")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: P&L Calculation API
    print("\n2. Testing P&L Calculation API...")
    try:
        response = requests.post(
            f"{base_url}/api/calculate-pl",
            json=lc_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            pl_data = response.json()
            
            if pl_data.get('success'):
                pl_result = pl_data.get('pl_result', {})
                risk_metrics = pl_data.get('risk_metrics', {})
                debug_info = pl_data.get('debug_info', {})
                
                print(f"   ✓ P&L Calculation SUCCESS!")
                print(f"   ✓ Debug Info:")
                print(f"     - Use Real Data: {debug_info.get('use_real_data', 'Unknown')}")
                print(f"     - Real Data Available: {debug_info.get('real_data_available', 'Unknown')}")
                print(f"     - Processing Path: {debug_info.get('processing_path', 'Unknown')}")
                print(f"     - Data Source: {debug_info.get('data_source', 'Unknown')}")
                print(f"     - Chart Data Points: {debug_info.get('chart_data_points', 0)}")
                print(f"     - LC Amount: ${debug_info.get('lc_amount', 0):,.2f}")
                print(f"     - Contract Rate: {debug_info.get('lc_contract_rate', 0):.4f}")
                print(f"     - Issue Date: {debug_info.get('issue_date', 'Unknown')}")
                print(f"     - Maturity Date: {debug_info.get('maturity_date', 'Unknown')}")
                print(f"   ✓ Data Source: {pl_result.get('data_source', 'Unknown')}")
                print(f"   ✓ Total P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
                print(f"   ✓ Current Rate: ₹{pl_result.get('spot_rate', 0):.4f}")
                print(f"   ✓ Original Rate: ₹{pl_result.get('original_rate', 0):.4f}")
                print(f"   ✓ P&L Percentage: {pl_result.get('pl_percentage', 0):.2f}%")
                print(f"   ✓ Days Remaining: {pl_result.get('days_remaining', 0)}")
                print(f"   ✓ Max Profit: ₹{pl_result.get('max_profit', 0):,.2f}")
                print(f"   ✓ Max Loss: ₹{pl_result.get('max_loss', 0):,.2f}")
                print(f"   ✓ Chart Data Points: {len(pl_result.get('chart_data', []))}")
                
                # Check if using real 2025 data
                actual_data_source = debug_info.get('data_source', 'Unknown')
                if actual_data_source == 'Real_2025_Market_Data':
                    print(f"   🎉 USING REAL 2025 MARKET DATA!")
                else:
                    print(f"   ⚠️  Using fallback data: {actual_data_source}")
                    print(f"   ⚠️  Real data check result: {debug_info.get('use_real_data', 'Unknown')}")
                
                # Validate meaningful results
                total_pl = pl_result.get('total_pl_inr', 0)
                if abs(total_pl) > 1000:  # At least ₹1,000 P&L
                    print(f"   ✓ Meaningful P&L results detected")
                else:
                    print(f"   ⚠️  P&L results may be too small")
                
            else:
                print(f"   ❌ API returned error: {pl_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Scenario Analysis API
    print("\n3. Testing Scenario Analysis API...")
    try:
        response = requests.post(
            f"{base_url}/api/scenario-analysis",
            json=lc_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            scenario_data = response.json()
            
            if scenario_data.get('success'):
                scenarios = scenario_data.get('scenarios', [])
                print(f"   ✓ Scenario Analysis SUCCESS!")
                print(f"   ✓ Scenarios Generated: {len(scenarios)}")
                
                for scenario in scenarios[:3]:  # Show first 3 scenarios
                    name = scenario.get('name', 'Unknown')
                    rate_change = scenario.get('rate_change', 0) * 100
                    new_rate = scenario.get('new_rate', 0)
                    pl_inr = scenario.get('pl_inr', 0)
                    impact = scenario.get('impact', 'Unknown')
                    
                    print(f"     {name}: Rate Change {rate_change:+.1f}%, "
                          f"New Rate ₹{new_rate:.2f}, P&L ₹{pl_inr:,.2f} ({impact})")
                
                # Check if scenarios have meaningful values
                meaningful_scenarios = [s for s in scenarios if abs(s.get('pl_inr', 0)) > 1000]
                if meaningful_scenarios:
                    print(f"   ✓ {len(meaningful_scenarios)} scenarios with meaningful P&L")
                else:
                    print(f"   ⚠️  Scenarios may have low impact values")
                    
            else:
                print(f"   ❌ Scenario analysis failed: {scenario_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Report Generation API
    print("\n4. Testing Report Generation API...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-report",
            json=lc_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            report_data = response.json()
            
            if report_data.get('success'):
                report = report_data.get('report', {})
                print(f"   ✓ Report Generation SUCCESS!")
                print(f"   ✓ LC ID: {report.get('lc_id', 'N/A')}")
                print(f"   ✓ Total Value: {report.get('total_value', 'N/A')}")
                print(f"   ✓ Days Remaining: {report.get('days_remaining', 'N/A')}")
                print(f"   ✓ Report Status: {report.get('status', 'N/A')}")
                print(f"   ✓ Generation Time: {report.get('generation_time', 'N/A')}")
                
                # Check for executive summary
                exec_summary = report.get('executive_summary', '')
                if exec_summary and exec_summary != '[object Object]':
                    print(f"   ✓ Executive Summary Generated")
                else:
                    print(f"   ⚠️  Executive Summary needs improvement")
                    
            else:
                print(f"   ❌ Report generation failed: {report_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL WEB API TESTS PASSED!")
    print("="*80)
    
    print(f"\n🎉 RESULTS SUMMARY:")
    print(f"  Real 2025 LC Amount: ${lc_data['amount_usd']:,}")
    print(f"  Period: {lc_data['issue_date']} to {lc_data['maturity_date']}")
    print(f"  Expected Data Source: Real_2025_Market_Data")
    print(f"  Final P&L: ₹{pl_result.get('total_pl_inr', 0):,.2f}")
    print(f"  P&L %: {pl_result.get('pl_percentage', 0):.2f}%")
    print(f"  Max Profit Potential: ₹{pl_result.get('max_profit', 0):,.2f}")
    print(f"  Chart Data Points: {len(pl_result.get('chart_data', []))}")
    
    # Final validation
    if (pl_result.get('data_source') == 'Real_2025_Market_Data' and 
        abs(pl_result.get('total_pl_inr', 0)) > 10000 and
        len(pl_result.get('chart_data', [])) > 50):
        print(f"\n🚀 SUCCESS: Real 2025 system is working perfectly!")
        return True
    else:
        print(f"\n⚠️  Some issues detected - please review the results")
        return False

if __name__ == "__main__":
    try:
        success = test_web_api_2025()
        if success:
            print("\n✅ Web API test completed successfully!")
        else:
            print("\n❌ Web API test found issues!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
