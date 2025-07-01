"""
Flask Web Application for Currency Risk Management System
Provides a web interface for calculating P&L and managing currency risk.
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
from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator
from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
from currency_risk_mgmt.reports.generator import ReportGenerator
from currency_risk_mgmt.reports.forward_reports import ForwardRatesReportGenerator

app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

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

@app.route('/api/forward-rates')
def get_forward_rates():
    """Get forward rates for different periods"""
    try:
        forward_provider = ForwardRatesProvider()
        
        rates = {}
        periods = [30, 60, 90, 180, 365]
        
        # Get current spot rate as base
        forex_provider = ForexDataProvider()
        spot_rate = forex_provider.get_current_rate('USD', 'INR')
        
        for days in periods:
            # Calculate forward rate with slight premium based on time to maturity
            time_premium = (days / 365) * 0.02  # 2% annual premium
            rate = spot_rate * (1 + time_premium)
            rates[f'{days}d'] = rate
        
        return jsonify({
            'success': True,
            'rates': rates,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate-pl', methods=['POST'])
def calculate_pl():
    """Calculate P&L for given LC parameters"""
    try:
        data = request.json
        print(f"DEBUG: Received data: {data}")
        
        # Create LC
        lc = LetterOfCredit(
            lc_id=data.get('lc_number', 'WEB-LC-001'),
            commodity=data.get('commodity', 'Export'),
            quantity=1000,
            unit='tons',
            rate_per_unit=float(data['amount_usd']) / 1000,
            currency='USD',
            signing_date=data['issue_date'],
            maturity_days=(datetime.strptime(data['maturity_date'], '%Y-%m-%d') - datetime.strptime(data['issue_date'], '%Y-%m-%d')).days,
            customer_country=data.get('beneficiary', 'Customer Country')
        )
        
        print(f"DEBUG: Created LC - {lc.lc_id}, Amount: ${lc.total_value}, Signing: {lc.signing_date}")
        
        # Calculate P&L - Always use forward rates for meaningful results
        calculator = ForwardPLCalculator()
        result = calculator.calculate_daily_forward_pl(lc, 'INR')
        
        # Debug: Print what we got
        print(f"DEBUG: Forward calculation result keys: {list(result.keys()) if result else 'None'}")
        if result:
            summary = result.get('summary', {})
            print(f"DEBUG: Summary keys: {list(summary.keys()) if summary else 'No summary'}")
            print(f"DEBUG: Current P&L: {summary.get('current_pl', 'N/A')}")
            print(f"DEBUG: Chart data points: {len(result.get('chart_data', []))}")
        
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
                'chart_data': result.get('chart_data', [])
            }
            print(f"DEBUG: Using forward P&L results - P&L: ₹{formatted_result['total_pl_inr']:,.2f}")
        else:
            print("DEBUG: Forward calculation failed, using fallback")
            # Fallback to spot calculation if forward calculation fails
            spot_calculator = ProfitLossCalculator()
            spot_result = spot_calculator.calculate_current_pl(lc, 'INR')
            
            formatted_result = {
                'total_pl_inr': spot_result.get('unrealized_pl', 0),
                'spot_rate': spot_result.get('current_rate', 85.0),
                'original_rate': spot_result.get('signing_rate', 85.0),
                'pl_percentage': spot_result.get('pl_percentage', 0),
                'days_remaining': lc.days_remaining,
                'chart_data': []
            }
            print(f"DEBUG: Using fallback P&L results - P&L: ₹{formatted_result['total_pl_inr']:,.2f}")
        
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
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"DEBUG: Exception in calculate_pl: {e}")
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
            customer_country=data.get('beneficiary', 'Customer Country')
        )
        
        # Get scenario parameters
        scenarios = data.get('scenarios', [
            {'name': 'Best Case', 'rate_change': 0.05},
            {'name': 'Base Case', 'rate_change': 0.0},
            {'name': 'Worst Case', 'rate_change': -0.05}
        ])
        
        # Enhanced scenario analysis using actual forward rate data
        calculator = ForwardPLCalculator()
        
        # First get the base forward P&L calculation
        base_result = calculator.calculate_daily_forward_pl(lc, 'INR')
        base_forward_rate = base_result.get('current_forward_rate', 85.0) if base_result else 85.0
        base_pl = base_result.get('summary', {}).get('current_pl', 0) if base_result else 0
        
        results = []
        
        for scenario in scenarios:
            # Calculate new rate based on scenario
            rate_change = scenario['rate_change']
            new_rate = base_forward_rate * (1 + rate_change)
            
            # Calculate P&L for this scenario
            new_pl = lc.total_value * (new_rate - base_result.get('signing_forward_rate', 85.0)) if base_result else 0
            pl_change = new_pl - base_pl
            
            # Determine impact level
            impact_percentage = abs(pl_change) / (lc.total_value * base_forward_rate) * 100 if base_forward_rate else 0
            if impact_percentage > 3:
                impact = "High Impact"
            elif impact_percentage > 1:
                impact = "Medium Impact"
            else:
                impact = "Low Impact"
            
            result = {
                'scenario_name': scenario['name'],
                'rate_change_percent': rate_change * 100,
                'new_rate': new_rate,
                'pl_inr': new_pl,
                'pl_change': pl_change,
                'impact': impact,
                'impact_percentage': impact_percentage
            }
            results.append(result)
        
        return jsonify({
            'success': True,
            'scenarios': results,
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
            customer_country=data.get('beneficiary', 'Customer Country')
        )
        
        # Generate comprehensive report using forward P&L analysis
        forward_calculator = ForwardPLCalculator()
        forward_result = forward_calculator.calculate_daily_forward_pl(lc, 'INR')
        
        if forward_result:
            summary = forward_result.get('summary', {})
            
            # Create meaningful report with actual data
            formatted_report = {
                'report_header': {
                    'generated_date': datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p'),
                    'lc_id': lc.lc_id,
                    'total_value_usd': lc.total_value,
                    'days_remaining': lc.days_remaining,
                    'currency_pair': f"{lc.currency}/INR"
                },
                'pl_analysis': {
                    'current_pl': summary.get('current_pl', 0),
                    'max_profit': summary.get('max_profit', 0),
                    'max_loss': summary.get('max_loss', 0),
                    'max_profit_date': summary.get('max_profit_date', ''),
                    'max_loss_date': summary.get('max_loss_date', ''),
                    'volatility': summary.get('volatility', 0),
                    'total_days_analyzed': summary.get('total_days', 0)
                },
                'forward_rates': {
                    'signing_rate': forward_result.get('signing_forward_rate', 0),
                    'current_rate': forward_result.get('current_forward_rate', 0),
                    'rate_change': forward_result.get('current_forward_rate', 0) - forward_result.get('signing_forward_rate', 0)
                },
                'risk_assessment': {
                    'current_pl_percentage': (summary.get('current_pl', 0) / (lc.total_value * forward_result.get('signing_forward_rate', 85.0))) * 100 if forward_result.get('signing_forward_rate') else 0,
                    'risk_level': 'HIGH' if abs(summary.get('current_pl', 0)) > lc.total_value * 0.05 else 'MEDIUM' if abs(summary.get('current_pl', 0)) > lc.total_value * 0.02 else 'LOW',
                    'recommendation': 'Consider hedging to lock in gains' if summary.get('current_pl', 0) > 0 else 'Monitor closely for recovery' if summary.get('current_pl', 0) < 0 else 'Position is neutral'
                },
                'executive_summary': {
                    'title': 'Daily Forward P&L Analysis',
                    'summary': f"Analysis of {lc.lc_id} shows current P&L of ₹{summary.get('current_pl', 0):,.2f} with maximum profit opportunity of ₹{summary.get('max_profit', 0):,.2f} and maximum risk exposure of ₹{summary.get('max_loss', 0):,.2f}.",
                    'days_analyzed': summary.get('total_days', 0),
                    'chart_data_points': len(forward_result.get('chart_data', []))
                },
                'metadata': {
                    'report_sections': 6,
                    'generation_time': datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p'),
                    'analysis_type': 'Forward P&L Analysis'
                }
            }
        else:
            # Fallback report if forward calculation fails
            formatted_report = {
                'report_header': {
                    'generated_date': datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p'),
                    'lc_id': lc.lc_id,
                    'total_value_usd': lc.total_value,
                    'days_remaining': lc.days_remaining,
                    'status': 'Fallback calculation used'
                },
                'executive_summary': {
                    'title': 'Basic LC Analysis',
                    'summary': 'Forward P&L calculation unavailable, using basic analysis.',
                    'recommendation': 'Enable forward rate analysis for detailed insights'
                }
            }
        
        return jsonify({
            'success': True,
            'report': formatted_report,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
