"""
Simple Flask app to test the real 2025 data integration.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.real_forward_pl_2025 import RealForwardPLCalculator2025

app = Flask(__name__)

@app.route('/')
def index():
    """Simple index page"""
    return '''
    <h1>Real 2025 Currency Risk Management System</h1>
    <p>Test endpoint for real 2025 forward rates data</p>
    <p><a href="/api/test-real-2025">Test Real 2025 Data</a></p>
    '''

@app.route('/api/test-real-2025', methods=['GET', 'POST'])
def test_real_2025():
    """Test endpoint for real 2025 data"""
    try:
        # Create test LC
        lc = LetterOfCredit(
            lc_id='TEST-2025-001',
            commodity='Test Export',
            quantity=1000,
            unit='tons',
            rate_per_unit=400,  # $400 per ton
            currency='USD',
            signing_date='2025-06-16',
            maturity_days=92,  # June 16 to Sep 16
            customer_country='Test Country',
            contract_rate=84.15  # Contract rate
        )
        
        # Test real data calculator
        calculator = RealForwardPLCalculator2025()
        
        # Check data availability
        data_available = calculator.is_real_data_available('2025-06-16', '2025-09-16')
        
        if data_available:
            # Calculate P&L
            daily_pl = calculator.calculate_daily_pl(lc, '2025-06-16')
            
            if daily_pl:
                final_pl = daily_pl[-1]
                
                result = {
                    'success': True,
                    'message': 'Real 2025 data is working!',
                    'data_source': 'Real_2025_Market_Data',
                    'lc_amount': lc.total_value,
                    'contract_rate': lc.contract_rate,
                    'final_forward_rate': final_pl.forward_rate,
                    'final_pl': final_pl.pl_amount,
                    'pl_percentage': final_pl.pl_percentage,
                    'data_points': len(daily_pl),
                    'test_timestamp': datetime.now().isoformat()
                }
            else:
                result = {
                    'success': False,
                    'message': 'Real 2025 data calculation failed - no daily P&L',
                    'data_available': data_available
                }
        else:
            result = {
                'success': False,
                'message': 'Real 2025 data not available',
                'data_available': data_available
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Exception occurred during testing'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # Use port 5001 to avoid conflicts
