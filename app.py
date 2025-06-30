"""
Flask Web Application for Currency Risk Management System
Provides a web interface for the comprehensive currency risk management features
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from datetime import datetime, timedelta
import json
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator
from currency_risk_mgmt.reports.generator import ReportGenerator
from currency_risk_mgmt.reports.forward_reports import ForwardRatesReportGenerator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

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
        
        for days in periods:
            maturity_date = datetime.now() + timedelta(days=days)
            forward_curve = forward_provider.get_forward_curve('USD', 'INR', datetime.now().strftime('%Y-%m-%d'))
            rate = forward_curve.get(f'{days}d', 85.0)  # Default fallback
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
    """Calculate P&L for a trade scenario"""
    try:
        data = request.json
        
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
        
        # Calculate P&L
        if data.get('use_forward_rates', False):
            calculator = ForwardPLCalculator()
            result = calculator.calculate_daily_forward_pl(lc, 'INR')
        else:
            calculator = ProfitLossCalculator()
            result = calculator.calculate_current_pl(lc, 'INR')
        
        # Calculate risk metrics
        risk_calculator = RiskMetricsCalculator()
        risk_metrics = risk_calculator.calculate_value_at_risk(lc, base_currency='INR')
        
        return jsonify({
            'success': True,
            'pl_result': result,
            'risk_metrics': risk_metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
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
        
        calculator = ForwardPLCalculator()
        results = []
        
        for scenario in scenarios:
            result = calculator.calculate_scenario_analysis(lc, scenario['rate_change'])
            result['scenario_name'] = scenario['name']
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
        
        # Generate report
        if data.get('include_forward_analysis', False):
            report_gen = ForwardRatesReportGenerator()
            report_data = report_gen.generate_comprehensive_report(lc, 'INR')
        else:
            report_gen = ReportGenerator()
            report_data = report_gen.generate_lc_summary_report(lc, 'INR')
        
        return jsonify({
            'success': True,
            'report': report_data,
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
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
