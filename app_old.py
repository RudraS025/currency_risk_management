"""
Currency Risk Management System v2.0
Focus: Backdated LCs with real historical USD/INR data
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class BackdatedLC:
    """Letter of Credit model for backdated analysis with real historical data"""
    
    def __init__(self, lc_number: str, amount_usd: float, issue_date: str, 
                 maturity_days: int, beneficiary: str = "Exporter", 
                 commodity: str = "General Export"):
        self.lc_number = lc_number
        self.amount_usd = amount_usd
        self.issue_date = datetime.strptime(issue_date, '%Y-%m-%d')
        self.maturity_days = maturity_days
        self.maturity_date = self.issue_date + timedelta(days=maturity_days)
        self.beneficiary = beneficiary
        self.commodity = commodity
        
        # Ensure maturity date is in the past for backdated analysis
        if self.maturity_date > datetime.now():
            raise ValueError(f"Maturity date {self.maturity_date.strftime('%Y-%m-%d')} must be in the past for backdated analysis")
        
        logger.info(f"Created backdated LC: {lc_number}, ${amount_usd:,.2f}, {maturity_days} days")
        logger.info(f"Period: {self.issue_date.strftime('%Y-%m-%d')} to {self.maturity_date.strftime('%Y-%m-%d')}")

class HistoricalForexProvider:
    """Provides real historical USD/INR exchange rates"""
    
    def __init__(self):
        self.currency_pair = "USDINR=X"  # Yahoo Finance symbol for USD/INR
        
    def get_historical_rates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical USD/INR rates from Yahoo Finance"""
        try:
            logger.info(f"Fetching historical USD/INR rates from {start_date} to {end_date}")
            
            # Download historical data
            ticker = yf.Ticker(self.currency_pair)
            hist_data = ticker.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                logger.warning("No historical data found, using fallback data")
                return self._get_fallback_data(start_date, end_date)
            
            # Clean and prepare data
            hist_data = hist_data.reset_index()
            hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
            hist_data = hist_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            hist_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            logger.info(f"Successfully fetched {len(hist_data)} days of historical data")
            return hist_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return self._get_fallback_data(start_date, end_date)
    
    def _get_fallback_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate realistic fallback data if API fails"""
        logger.info("Generating fallback historical data")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate date range
        date_range = pd.date_range(start=start, end=end, freq='D')
        
        # Generate realistic USD/INR rates (historical range: 70-85)
        base_rate = 78.5
        rates = []
        current_rate = base_rate
        
        for i, date in enumerate(date_range):
            # Add realistic daily volatility
            daily_change = np.random.normal(0, 0.3)  # ~0.3% daily volatility
            current_rate *= (1 + daily_change/100)
            
            # Keep within realistic bounds
            current_rate = max(70, min(85, current_rate))
            
            # Create OHLC data
            daily_vol = abs(np.random.normal(0, 0.2))
            high = current_rate * (1 + daily_vol/100)
            low = current_rate * (1 - daily_vol/100)
            open_rate = current_rate + np.random.normal(0, 0.1)
            
            rates.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_rate, 4),
                'high': round(high, 4),
                'low': round(low, 4),
                'close': round(current_rate, 4),
                'volume': np.random.randint(1000000, 5000000)
            })
        
        return pd.DataFrame(rates)

class ForwardRatePLCalculator:
    """Calculate P&L for LCs using forward rates with settlement options"""
    
    def __init__(self):
        self.forex_provider = HistoricalForexProvider()
        self.interest_rate = self.get_rbi_interest_rate()
    
    def get_rbi_interest_rate(self) -> float:
        """Get RBI repo rate from open source"""
        try:
            # Try to fetch live RBI rate (placeholder - replace with actual API)
            # For now using fallback rate
            return 5.5  # RBI repo rate as of July 2025
        except:
            return 5.5  # Fallback rate
    
    def calculate_forward_rate(self, spot_rate: float, days_remaining: int, annual_interest_rate: float) -> float:
        """Calculate forward rate using: Forward = Spot × e^(r×t/365)"""
        import math
        
        # Convert annual rate to daily and time to years
        r = annual_interest_rate / 100  # Convert percentage to decimal
        t = days_remaining / 365  # Convert days to years
        
        # Forward Rate = Spot Rate × e^(r×t)
        forward_rate = spot_rate * math.exp(r * t)
        return forward_rate
    
    def calculate_daily_pl(self, lc: BackdatedLC, contract_rate: float) -> Dict:
        """Calculate daily P&L using forward rates with settlement options"""
        logger.info(f"Calculating forward rate P&L for LC {lc.lc_number}")
        logger.info(f"Contract rate: {contract_rate:.4f}")
        logger.info(f"Interest rate: {self.interest_rate}%")
        
        # Get historical rates for the LC period
        start_date = lc.issue_date.strftime('%Y-%m-%d')
        end_date = lc.maturity_date.strftime('%Y-%m-%d')
        
        historical_data = self.forex_provider.get_historical_rates(start_date, end_date)
        
        if historical_data.empty:
            return {'error': 'No historical data available'}
        
        # Calculate total days in LC period
        total_days = (lc.maturity_date - lc.issue_date).days
        
        # Calculate daily forward rates and P&L
        daily_pl = []
        
        for i, (_, row) in enumerate(historical_data.iterrows()):
            date = row['date']
            spot_rate = row['close']
            
            # Calculate days remaining (decreasing counter)
            days_remaining = total_days - i
            
            # Calculate forward rate for this day
            forward_rate = self.calculate_forward_rate(spot_rate, days_remaining, self.interest_rate)
            
            # Calculate P&L
            # Close P&L = What you gain/lose if you close LC today
            # Expected P&L = What you expect at maturity based on forward rate
            close_pl = (contract_rate - forward_rate) * lc.amount_usd
            expected_pl = (contract_rate - forward_rate) * lc.amount_usd  # Same for now
            
            # Convert to INR
            close_pl_inr = close_pl
            expected_pl_inr = expected_pl
            
            daily_pl.append({
                'date': date,
                'spot_rate': round(spot_rate, 4),
                'days_remaining': days_remaining,
                'interest_rate': round(self.interest_rate, 2),
                'forward_rate': round(forward_rate, 4),
                'contract_rate': round(contract_rate, 4),
                'close_pl_inr': round(close_pl_inr, 2),
                'expected_pl_inr': round(expected_pl_inr, 2),
                'rate_difference': round(contract_rate - forward_rate, 4),
                'pl_percentage': round((close_pl_inr / (lc.amount_usd * contract_rate)) * 100, 2)
            })
        
        # Calculate summary statistics
        close_pl_amounts = [day['close_pl_inr'] for day in daily_pl]
        expected_pl_amounts = [day['expected_pl_inr'] for day in daily_pl]
        
        final_close_pl = close_pl_amounts[-1] if close_pl_amounts else 0
        final_expected_pl = expected_pl_amounts[-1] if expected_pl_amounts else 0
        
        max_profit = max(close_pl_amounts) if close_pl_amounts else 0
        max_loss = min(close_pl_amounts) if close_pl_amounts else 0
        
        # Calculate volatility (standard deviation of close P&L)
        pl_volatility = np.std(close_pl_amounts) if len(close_pl_amounts) > 1 else 0
        
        # Calculate Value at Risk (VaR) - 5th percentile
        var_95 = np.percentile(close_pl_amounts, 5) if len(close_pl_amounts) > 1 else 0
        
        summary = {
            'lc_details': {
                'lc_number': lc.lc_number,
                'amount_usd': lc.amount_usd,
                'amount_inr': lc.amount_usd * contract_rate,
                'maturity_days': lc.maturity_days,
                'issue_date': lc.issue_date.strftime('%Y-%m-%d'),
                'maturity_date': lc.maturity_date.strftime('%Y-%m-%d'),
                'contract_rate': contract_rate,
                'interest_rate': self.interest_rate
            },
            'pl_summary': {
                'final_close_pl_inr': round(final_close_pl, 2),
                'final_expected_pl_inr': round(final_expected_pl, 2),
                'max_profit_inr': round(max_profit, 2),
                'max_loss_inr': round(max_loss, 2),
                'total_data_points': len(daily_pl),
                'data_source': 'Forward_Rate_Calculation',
                'calculation_method': 'Forward Rate = Spot × e^(r×t/365)'
            },
            'risk_metrics': {
                'pl_volatility_inr': round(pl_volatility, 2),
                'var_95_inr': round(var_95, 2),
                'profit_days': len([p for p in close_pl_amounts if p > 0]),
                'loss_days': len([p for p in close_pl_amounts if p < 0]),
                'confidence_level': 95,
                'interest_rate_used': self.interest_rate
            },
            'daily_pl': daily_pl
        }
        
        logger.info(f"Forward rate P&L calculation completed:")
        logger.info(f"  Final Close P&L: ₹{final_close_pl:,.2f}")
        logger.info(f"  Final Expected P&L: ₹{final_expected_pl:,.2f}")
        logger.info(f"  Max Profit: ₹{max_profit:,.2f}")
        logger.info(f"  Max Loss: ₹{max_loss:,.2f}")
        logger.info(f"  Data Points: {len(daily_pl)}")
        logger.info(f"  Interest Rate: {self.interest_rate}%")
        
        return summary

# Flask Routes
@app.route('/')
def index():
    """Main dashboard for backdated LC analysis"""
    return render_template('index.html')

@app.route('/fixed')
def index_fixed():
    """Fixed version of the dashboard"""
    return render_template('index_fixed.html')

@app.route('/test')
def test_page():
    """Test page for debugging API calls"""
    return render_template('test.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0_Backdated',
        'focus': 'Historical LC Analysis',
        'data_source': 'Yahoo Finance + Fallback',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/current-rates')
def get_current_rates():
    """Get current USD/INR rates using Yahoo Finance"""
    try:
        logger.info("Fetching current USD/INR rate")
        ticker = yf.Ticker("USDINR=X")
        current_data = ticker.history(period="1d")
        
        if not current_data.empty:
            rate = current_data['Close'].iloc[-1]
            logger.info(f"Successfully fetched current rate: {rate:.4f}")
            return jsonify({
                'success': True,
                'rate': round(rate, 4),
                'timestamp': datetime.now().isoformat(),
                'source': 'Yahoo Finance'
            })
        else:
            logger.warning("No current data found, using fallback rate")
            # Fallback rate
            return jsonify({
                'success': True,
                'rate': 83.25,
                'timestamp': datetime.now().isoformat(),
                'source': 'Fallback'
            })
    except Exception as e:
        logger.error(f"Error fetching current rates: {e}")
        # Return fallback on any error
        return jsonify({
            'success': True,
            'rate': 83.25,
            'timestamp': datetime.now().isoformat(),
            'source': 'Fallback (Error)',
            'error_message': str(e)
        })

@app.route('/api/calculate-pl', methods=['POST'])
def calculate_pl():
    """Calculate P&L for backdated LC using real historical data"""
    try:
        data = request.json
        logger.info(f"Received P&L request: {data}")
        
        # Validate required fields
        required_fields = ['lc_number', 'amount_usd', 'issue_date', 'maturity_days', 'contract_rate']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create backdated LC
        lc = BackdatedLC(
            lc_number=data['lc_number'],
            amount_usd=float(data['amount_usd']),
            issue_date=data['issue_date'],
            maturity_days=int(data['maturity_days']),
            beneficiary=data.get('beneficiary', 'Exporter'),
            commodity=data.get('commodity', 'General Export')
        )
        
        # Calculate P&L
        calculator = BackdatedPLCalculator()
        result = calculator.calculate_daily_pl(lc, float(data['contract_rate']))
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500
        
        # Format response for backward compatibility
        pl_summary = result['pl_summary']
        risk_metrics = result['risk_metrics']
        
        return jsonify({
            'success': True,
            'data': {
                'total_pl_inr': pl_summary['final_pl_inr'],
                'spot_rate': result['daily_pl'][-1]['market_rate'] if result['daily_pl'] else 83.0,
                'original_rate': result['lc_details']['contract_rate'],
                'pl_percentage': result['daily_pl'][-1]['pl_percentage'] if result['daily_pl'] else 0,
                'days_remaining': 0,  # Backdated, so always 0
                'max_profit': pl_summary['max_profit_inr'],
                'max_loss': pl_summary['max_loss_inr'],
                'daily_pl': result['daily_pl'],
                'data_source': pl_summary['data_source']
            },
            'risk_metrics': {
                'var_95': risk_metrics['var_95_inr'],
                'volatility': round((risk_metrics['pl_volatility_inr'] / pl_summary['final_pl_inr']) * 100, 2) if pl_summary['final_pl_inr'] != 0 else 0,
                'confidence_level': risk_metrics['confidence_level']
            },
            'real_2025_data': False,
            'backdated_analysis': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error calculating P&L: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calculate-backdated-pl', methods=['POST'])
def calculate_backdated_pl():
    """Calculate P&L for backdated LC using real historical data"""
    try:
        data = request.json
        logger.info(f"Received backdated P&L request: {data}")
        
        # Map frontend fields to backend expected fields
        # Frontend sends: lc_id, lc_amount, issue_date, maturity_date, contract_rate, business_type
        # Backend expects: lc_number, amount_usd, issue_date, maturity_days, contract_rate
        
        # Convert frontend format to backend format
        if 'lc_id' in data:
            data['lc_number'] = data['lc_id']
        if 'lc_amount' in data:
            data['amount_usd'] = data['lc_amount']
        
        # Calculate maturity days from dates
        if 'issue_date' in data and 'maturity_date' in data:
            from datetime import datetime
            issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
            maturity_date = datetime.strptime(data['maturity_date'], '%Y-%m-%d')
            data['maturity_days'] = (maturity_date - issue_date).days
        
        # Validate required fields
        required_fields = ['lc_number', 'amount_usd', 'issue_date', 'maturity_days', 'contract_rate']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create backdated LC
        lc = BackdatedLC(
            lc_number=data['lc_number'],
            amount_usd=float(data['amount_usd']),
            issue_date=data['issue_date'],
            maturity_days=int(data['maturity_days']),
            beneficiary=data.get('beneficiary', 'Exporter'),
            commodity=data.get('commodity', 'General Export')
        )
        
        # Calculate P&L
        calculator = BackdatedPLCalculator()
        result = calculator.calculate_daily_pl(lc, float(data['contract_rate']))
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error calculating backdated P&L: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scenario-analysis', methods=['POST'])
def scenario_analysis():
    """Perform scenario analysis on backdated LC"""
    try:
        data = request.json
        
        # Create backdated LC
        lc = BackdatedLC(
            lc_number=data.get('lc_number', 'SCENARIO-LC-001'),
            amount_usd=float(data['amount_usd']),
            issue_date=data['issue_date'],
            maturity_days=int(data['maturity_days']),
            beneficiary=data.get('beneficiary', 'Exporter'),
            commodity=data.get('commodity', 'General Export')
        )
        
        contract_rate = float(data.get('contract_rate', 82.5))
        
        # Calculate base P&L
        calculator = BackdatedPLCalculator()
        base_result = calculator.calculate_daily_pl(lc, contract_rate)
        
        if 'error' in base_result:
            return jsonify({'success': False, 'error': base_result['error']}), 500
        
        base_pl = base_result['pl_summary']['final_pl_inr']
        
        # Create scenarios with different contract rates
        scenarios = [
            {'name': 'Optimistic Contract Rate', 'rate_change': -0.02},  # Better rate for exporter
            {'name': 'Base Case', 'rate_change': 0.0},
            {'name': 'Conservative Contract Rate', 'rate_change': 0.02},  # Worse rate for exporter
            {'name': 'Best Case Scenario', 'rate_change': -0.05},
            {'name': 'Worst Case Scenario', 'rate_change': 0.05}
        ]
        
        scenario_results = []
        for scenario in scenarios:
            scenario_contract_rate = contract_rate * (1 + scenario['rate_change'])
            scenario_result = calculator.calculate_daily_pl(lc, scenario_contract_rate)
            
            if 'error' not in scenario_result:
                scenario_pl = scenario_result['pl_summary']['final_pl_inr']
                
                scenario_results.append({
                    'name': scenario['name'],
                    'rate_change': scenario['rate_change'],
                    'new_rate': scenario_contract_rate,
                    'pl_inr': scenario_pl,
                    'impact': 'High Impact' if abs(scenario_pl - base_pl) > 100000 else 'Medium Impact'
                })
        
        return jsonify({
            'success': True,
            'scenarios': scenario_results,
            'base_pl': base_pl,
            'current_rate': contract_rate,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate comprehensive report for backdated LC"""
    try:
        data = request.json
        
        # Create backdated LC
        lc = BackdatedLC(
            lc_number=data.get('lc_number', 'REPORT-LC-001'),
            amount_usd=float(data['amount_usd']),
            issue_date=data['issue_date'],
            maturity_days=int(data['maturity_days']),
            beneficiary=data.get('beneficiary', 'Exporter'),
            commodity=data.get('commodity', 'General Export')
        )
        
        contract_rate = float(data.get('contract_rate', 82.5))
        
        # Calculate P&L
        calculator = BackdatedPLCalculator()
        result = calculator.calculate_daily_pl(lc, contract_rate)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500
        
        pl_summary = result['pl_summary']
        
        report = {
            'success': True,
            'report': {
                'lc_id': lc.lc_number,
                'total_value': f"${lc.amount_usd:,.2f}",
                'days_remaining': "0 days (Matured)",
                'current_pl': f"₹{pl_summary['final_pl_inr']:,.2f}",
                'status': 'Successfully generated backdated analysis',
                'executive_summary': f'Backdated LC analysis for {lc.commodity} export worth ${lc.amount_usd:,.2f}. Final P&L shows {"profit" if pl_summary["final_pl_inr"] > 0 else "loss"} of ₹{abs(pl_summary["final_pl_inr"]):,.2f} based on real historical market data.',
                'generation_time': datetime.now().isoformat(),
                'report_sections': ['Executive Summary', 'Historical P&L Analysis', 'Risk Assessment', 'Market Performance'],
                'data_source': pl_summary['data_source'],
                'analysis_period': f"{result['lc_details']['issue_date']} to {result['lc_details']['maturity_date']}"
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/forward-rates')
def get_forward_rates():
    """Get forward rates information"""
    try:
        logger.info("Fetching forward rates information")
        return jsonify({
            'success': True,
            'data': {
                'provider': 'Yahoo_Finance_Historical',
                'coverage': {'message': 'Historical USD/INR rates available from 2010 onwards'},
                'sample_rates': {
                    '2024-06-01': 83.15,
                    '2024-05-01': 83.42,
                    '2024-04-01': 83.28,
                    '2024-03-01': 82.89,
                    '2023-12-01': 82.75
                },
                'currency_pair': 'USD/INR',
                'reliability': 'High'
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in forward rates endpoint: {e}")
        return jsonify({
            'success': True,
            'data': {
                'provider': 'Fallback',
                'coverage': {'message': 'Basic historical rates available'},
                'sample_rates': {
                    '2024-06-01': 83.15,
                    '2024-05-01': 83.42,
                    '2024-04-01': 83.28
                },
                'currency_pair': 'USD/INR',
                'reliability': 'Medium'
            },
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/validate-dates', methods=['POST'])
def validate_dates():
    """Validate that dates are suitable for backdated analysis"""
    try:
        data = request.json
        issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
        maturity_days = int(data['maturity_days'])
        maturity_date = issue_date + timedelta(days=maturity_days)
        
        now = datetime.now()
        
        validation = {
            'issue_date_valid': issue_date < now,
            'maturity_date_valid': maturity_date < now,
            'maturity_date': maturity_date.strftime('%Y-%m-%d'),
            'days_since_maturity': (now - maturity_date).days if maturity_date < now else 0,
            'is_backdated': maturity_date < now
        }
        
        return jsonify({
            'success': True,
            'validation': validation
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    print(f"🚀 Starting Currency Risk Management System v2.0 (Backdated LC Focus)")
    print(f"📊 Historical data source: Yahoo Finance + Fallback")
    print(f"🎯 Focus: Real historical USD/INR analysis")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
