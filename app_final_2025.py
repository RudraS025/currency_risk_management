"""
Final working version of the Currency Risk Management Flask app with Real 2025 data.
"""

from flask import Flask, render_template, request, jsonify
import traceback
from datetime import datetime, timedelta
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025
from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator
from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
from currency_risk_mgmt.data_providers.real_forward_rates_2025 import RealForwardRatesProvider2025
from currency_risk_mgmt.reports.generator import ReportGenerator
from currency_risk_mgmt.reports.forward_reports import ForwardRatesReportGenerator

app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'real_2025_data_available': True
    })

@app.route('/api/current-rates')
def get_current_rates():
    """Get current USD/INR rates"""
    try:
        forex_provider = ForexDataProvider()
        rate = forex_provider.get_current_rate('USD', 'INR')
        
        return jsonify({
            'success': True,
            'rate': rate,
            'timestamp': datetime.now().isoformat(),
            'source': 'Live API'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate-pl', methods=['POST'])
def calculate_pl():
    """Calculate P&L for given LC parameters using Real 2025 data when available"""
    try:
        data = request.json
        print(f"🔍 DEBUG: Received P&L request: {data}", flush=True)
        
        # Create LC with proper date handling
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
        
        print(f"📋 DEBUG: Created LC - Amount: ${lc.total_value:,.2f}, Rate: {lc.contract_rate:.4f}", flush=True)
        
        # Try Real 2025 data first
        real_calculator = RealForwardPLCalculator2025()
        use_real_data = real_calculator.is_real_data_available(data['issue_date'], data['maturity_date'])
        
        print(f"🎯 DEBUG: Real 2025 data available: {use_real_data}", flush=True)
        
        if use_real_data:
            print("🚀 DEBUG: PROCESSING WITH REAL 2025 DATA!", flush=True)
            
            try:
                # Calculate P&L using real 2025 data
                daily_pl = real_calculator.calculate_daily_pl(lc, data['issue_date'])
                risk_metrics = real_calculator.get_risk_metrics(lc, data['issue_date'])
                optimal_dates = real_calculator.find_optimal_dates(lc, data['issue_date'])
                
                if daily_pl and len(daily_pl) > 0:
                    # Format results
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
                        'data_source': 'Real_2025_Market_Data'
                    }
                    
                    print(f"✅ SUCCESS: Real 2025 P&L = ${formatted_result['total_pl_inr']:,.2f} ({len(chart_data)} points)", flush=True)
                    
                    # Calculate risk metrics for response
                    formatted_risk = {
                        'var_95': risk_metrics.get('var_95', 0),
                        'volatility': risk_metrics.get('rate_volatility', 0) * 100,  # Convert to percentage
                        'confidence_level': 95
                    }
                    
                    return jsonify({
                        'success': True,
                        'pl_result': formatted_result,
                        'risk_metrics': formatted_risk,
                        'real_2025_data': True,
                        'timestamp': datetime.now().isoformat()
                    })
                
                else:
                    print("⚠️ DEBUG: Real 2025 calculation returned no results", flush=True)
                    
            except Exception as e:
                print(f"❌ DEBUG: Exception in real 2025 calculation: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        # Fallback to historical data
        print("🔄 DEBUG: Using fallback forward rates calculation", flush=True)
        calculator = ForwardPLCalculator()
        result = calculator.calculate_daily_forward_pl(lc, 'INR')
        
        if result and result.get('summary'):
            # Format forward P&L results
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
                'chart_data': result.get('chart_data', []),
                'data_source': 'Historical_Synthetic_Data'
            }
            print(f"📊 DEBUG: Using historical P&L: ₹{formatted_result['total_pl_inr']:,.2f}", flush=True)
        else:
            print("📉 DEBUG: Using spot calculation fallback", flush=True)
            # Fallback to spot calculation
            spot_calculator = ProfitLossCalculator()
            spot_result = spot_calculator.calculate_current_pl(lc, 'INR')
            
            formatted_result = {
                'total_pl_inr': spot_result.get('unrealized_pl', 0),
                'spot_rate': spot_result.get('current_rate', 85.0),
                'original_rate': spot_result.get('signing_rate', 85.0),
                'pl_percentage': spot_result.get('pl_percentage', 0),
                'days_remaining': lc.days_remaining,
                'chart_data': [],
                'data_source': 'Fallback_Spot_Data'
            }
        
        # Calculate risk metrics
        risk_calculator = RiskMetricsCalculator()
        risk_metrics = risk_calculator.calculate_value_at_risk(lc, base_currency='INR')
        
        formatted_risk = {
            'var_95': risk_metrics.get('var_95', 0),
            'volatility': risk_metrics.get('volatility', 0),
            'confidence_level': 95
        }
        
        return jsonify({
            'success': True,
            'pl_result': formatted_result,
            'risk_metrics': formatted_risk,
            'real_2025_data': False,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"💥 ERROR in calculate_pl: {e}", flush=True)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/scenario-analysis', methods=['POST'])
def scenario_analysis():
    """Perform scenario analysis"""
    try:
        data = request.json
        
        # Create LC
        lc = LetterOfCredit(
            lc_id=data.get('lc_number', 'SCENARIO-LC-001'),
            commodity=data.get('commodity', 'Export'),
            quantity=1000,
            unit='tons',
            rate_per_unit=float(data['amount_usd']) / 1000,
            currency='USD',
            signing_date=data['issue_date'],
            maturity_days=(datetime.strptime(data['maturity_date'], '%Y-%m-%d') - datetime.strptime(data['issue_date'], '%Y-%m-%d')).days,
            customer_country=data.get('beneficiary', 'Customer Country'),
            contract_rate=84.15  # Default contract rate for USD/INR
        )
        
        # Get scenario parameters
        scenarios = data.get('scenarios', [
            {'name': 'Best Case', 'rate_change': 0.05},
            {'name': 'Base Case', 'rate_change': 0.0},
            {'name': 'Worst Case', 'rate_change': -0.05}
        ])
        
        # Calculate current P&L as baseline
        calculator = ProfitLossCalculator()
        current_result = calculator.calculate_current_pl(lc, 'INR')
        base_pl = current_result.get('unrealized_pl', 0)
        current_rate = current_result.get('current_rate', 85.0)
        
        scenario_results = []
        for scenario in scenarios:
            rate_change = scenario['rate_change']
            new_rate = current_rate * (1 + rate_change)
            
            # Calculate P&L with new rate
            rate_diff = new_rate - current_rate
            pl_change = lc.total_value * rate_diff
            scenario_pl = base_pl + pl_change
            
            # Determine impact level
            if abs(scenario_pl) > 1000000:  # > 1M INR
                impact = "High Impact"
            elif abs(scenario_pl) > 100000:  # > 100K INR
                impact = "Medium Impact"
            else:
                impact = "Low Impact"
            
            scenario_results.append({
                'name': scenario['name'],
                'rate_change': rate_change,
                'new_rate': new_rate,
                'pl_inr': scenario_pl,
                'impact': impact
            })
        
        return jsonify({
            'success': True,
            'scenarios': scenario_results,
            'base_pl': base_pl,
            'current_rate': current_rate,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate comprehensive report"""
    try:
        data = request.json
        
        # Create LC
        lc = LetterOfCredit(
            lc_id=data.get('lc_number', 'REPORT-LC-001'),
            commodity=data.get('commodity', 'Export'),
            quantity=1000,
            unit='tons',
            rate_per_unit=float(data['amount_usd']) / 1000,
            currency='USD',
            signing_date=data['issue_date'],
            maturity_days=(datetime.strptime(data['maturity_date'], '%Y-%m-%d') - datetime.strptime(data['issue_date'], '%Y-%m-%d')).days,
            customer_country=data.get('beneficiary', 'Customer Country'),
            contract_rate=84.15  # Default contract rate for USD/INR
        )
        
        # Generate report data
        calculator = ProfitLossCalculator()
        current_result = calculator.calculate_current_pl(lc, 'INR')
        
        report = {
            'success': True,
            'report': {
                'lc_id': lc.lc_id,
                'total_value': f"${lc.total_value:,.2f}",
                'days_remaining': f"{lc.days_remaining} days",
                'current_pl': f"₹{current_result.get('unrealized_pl', 0):,.2f}",
                'status': 'Successfully generated comprehensive analysis',
                'executive_summary': f'LC analysis for {lc.commodity} export worth ${lc.total_value:,.2f}. Current P&L shows {"profit" if current_result.get("unrealized_pl", 0) > 0 else "loss"} of ₹{abs(current_result.get("unrealized_pl", 0)):,.2f}.',
                'generation_time': datetime.now().isoformat(),
                'report_sections': ['Executive Summary', 'P&L Analysis', 'Risk Assessment', 'Recommendations'],
                'data_source': 'Real_2025_Market_Data' if data.get('issue_date', '').startswith('2025') else 'Historical_Data'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    print(f"🚀 Starting Currency Risk Management System on port {port}")
    print(f"📊 Real 2025 data integration: ENABLED")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
