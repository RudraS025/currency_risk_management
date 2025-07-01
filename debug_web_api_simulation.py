"""
Test to simulate the exact web API call and see what happens with real 2025 data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025
from datetime import datetime

def simulate_web_api_call():
    """Simulate the exact web API call logic."""
    
    print("="*80)
    print("SIMULATING WEB API CALL WITH REAL 2025 DATA")
    print("="*80)
    
    # Simulate the exact data from the web API test
    data = {
        "lc_number": "REAL-2025-SONA-MASURI",
        "commodity": "SONA MASURI Rice Export",
        "amount_usd": 400000,
        "issue_date": "2025-06-16",
        "maturity_date": "2025-09-16",
        "beneficiary": "GTC IRAN"
    }
    
    print(f"Input Data: {data}")
    
    try:
        # Create LC with proper date handling (same as web API)
        issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
        maturity_date = datetime.strptime(data['maturity_date'], '%Y-%m-%d')
        maturity_days = (maturity_date - issue_date).days
        
        lc = LetterOfCredit(
            lc_id=data.get('lc_number', 'WEB-LC-001'),
            commodity=data.get('commodity', 'Export'),
            quantity=1000,
            unit='tons',
            rate_per_unit=float(data['amount_usd']) / 1000,
            currency='USD',
            signing_date=data['issue_date'],
            maturity_days=maturity_days,
            customer_country=data.get('beneficiary', 'Customer Country'),
            contract_rate=84.15  # Default contract rate for USD/INR
        )
        
        print(f"Created LC - {lc.lc_id}, Amount: ${lc.total_value}, Signing: {lc.signing_date}")
        print(f"Maturity days: {lc.maturity_days}, Contract rate: {lc.contract_rate}")
        print(f"Issue date: {issue_date}, Maturity date: {maturity_date}")
        
        # Check if we should use real 2025 data (same as web API)
        real_calculator = RealForwardPLCalculator2025()
        use_real_data = real_calculator.is_real_data_available(data['issue_date'], data['maturity_date'])
        
        print(f"Real data available: {use_real_data}")
        
        if use_real_data:
            print("Using REAL 2025 forward rates data")
            
            # Calculate P&L using real 2025 data
            try:
                daily_pl = real_calculator.calculate_daily_pl(lc, data['issue_date'])
                print(f"Daily P&L calculated: {len(daily_pl) if daily_pl else 0} data points")
                
                if daily_pl:
                    print("First few P&L points:")
                    for i, pl in enumerate(daily_pl[:3]):
                        print(f"  {i+1}. {pl.date}: Rate={pl.forward_rate:.4f}, P&L=${pl.pl_amount:,.2f}")
                    
                    final_pl = daily_pl[-1]
                    print(f"Final P&L: {final_pl.date}: Rate={final_pl.forward_rate:.4f}, P&L=${final_pl.pl_amount:,.2f}")
                else:
                    print("ERROR: No daily P&L calculated")
                    return False
                
            except Exception as e:
                print(f"ERROR calculating daily P&L: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            try:
                scenarios = real_calculator.calculate_scenario_analysis(lc, data['issue_date'])
                print(f"Scenarios calculated: {len(scenarios) if scenarios else 0}")
            except Exception as e:
                print(f"ERROR calculating scenarios: {e}")
                scenarios = []
            
            try:
                risk_metrics = real_calculator.get_risk_metrics(lc, data['issue_date'])
                print(f"Risk metrics calculated: {len(risk_metrics) if risk_metrics else 0} metrics")
                if risk_metrics:
                    print(f"  Max Profit: ${risk_metrics.get('max_profit', 0):,.2f}")
                    print(f"  Max Loss: ${risk_metrics.get('max_loss', 0):,.2f}")
            except Exception as e:
                print(f"ERROR calculating risk metrics: {e}")
                risk_metrics = {}
            
            try:
                optimal_dates = real_calculator.find_optimal_dates(lc, data['issue_date'])
                print(f"Optimal dates calculated: {len(optimal_dates) if optimal_dates else 0} dates")
            except Exception as e:
                print(f"ERROR calculating optimal dates: {e}")
                optimal_dates = {}
            
            if daily_pl:
                # Format results (same as web API)
                chart_data = [
                    {
                        'date': pl.date,
                        'forward_rate': pl.forward_rate,
                        'pl_amount': pl.pl_amount,
                        'cumulative_pl': pl.cumulative_pl,
                        'days_to_maturity': pl.days_to_maturity
                    }
                    for pl in daily_pl
                ]
                
                final_pl = daily_pl[-1]
                
                formatted_result = {
                    'total_pl_inr': final_pl.pl_amount,
                    'spot_rate': final_pl.forward_rate,
                    'original_rate': lc.contract_rate,
                    'pl_percentage': final_pl.pl_percentage,
                    'days_remaining': final_pl.days_to_maturity,
                    'max_profit': risk_metrics.get('max_profit', 0),
                    'max_loss': risk_metrics.get('max_loss', 0),
                    'max_profit_date': optimal_dates.get('max_profit', ('', 0))[0],
                    'max_loss_date': optimal_dates.get('max_loss', ('', 0))[0],
                    'volatility': risk_metrics.get('rate_volatility', 0),
                    'chart_data': chart_data,
                    'data_source': 'Real_2025_Market_Data',
                    'scenarios': [
                        {
                            'name': s.scenario_name,
                            'final_pl': s.final_pl,
                            'max_profit': s.max_profit,
                            'max_loss': s.max_loss,
                            'rate_shift': s.rate_shift
                        }
                        for s in scenarios
                    ]
                }
                
                print(f"RESULTS:")
                print(f"  Data Source: {formatted_result['data_source']}")
                print(f"  Final P&L: ${formatted_result['total_pl_inr']:,.2f}")
                print(f"  P&L Percentage: {formatted_result['pl_percentage']:.2f}%")
                print(f"  Max Profit: ${formatted_result['max_profit']:,.2f}")
                print(f"  Max Loss: ${formatted_result['max_loss']:,.2f}")
                print(f"  Chart Data Points: {len(formatted_result['chart_data'])}")
                print(f"  Scenarios: {len(formatted_result['scenarios'])}")
                
                print("\n✅ SUCCESS: Real 2025 data processing completed!")
                return True
                
            else:
                print("FAILURE: Daily P&L calculation returned empty results")
                return False
        
        else:
            print("Real data not available - would use fallback")
            return False
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_web_api_call()
    if success:
        print("\n🎉 Simulation successful - Real 2025 data should work in web API!")
    else:
        print("\n❌ Simulation failed - There's an issue with Real 2025 data processing")
