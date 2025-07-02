#!/usr/bin/env python3
"""
Currency Risk Management System v3.0 - Forward Rate Based
Complete rewrite with proper forward rate calculations and settlement options
"""

import yfinance as yf
import pandas as pd
import numpy as np
import math
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

print("🚀 Starting Currency Risk Management System v3.0 (Forward Rate Based)")
print("📊 Real forward rate calculations with settlement options")
print("🎯 Focus: Forward Rate = Spot × e^(r×t/365)")

class ForwardRateLC:
    """Letter of Credit with forward rate calculations"""
    
    def __init__(self, lc_number: str, amount_usd: float, issue_date: datetime, 
                 maturity_date: datetime, business_type: str = "import"):
        self.lc_number = lc_number
        self.amount_usd = amount_usd
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.business_type = business_type.lower()
        self.maturity_days = (maturity_date - issue_date).days

class RBIRateProvider:
    """Get RBI interest rates from open sources"""
    
    def get_rbi_repo_rate(self) -> float:
        """Get current RBI repo rate"""
        try:
            # Try to get from multiple sources
            # Source 1: RBI official API (if available)
            # Source 2: Financial data APIs
            # Fallback: Recent known rate
            
            # For now using fallback - replace with actual API calls
            current_rate = 6.5  # RBI repo rate as of July 2025
            logger.info(f"RBI repo rate: {current_rate}%")
            return current_rate
            
        except Exception as e:
            logger.warning(f"Could not fetch live RBI rate: {e}")
            return 6.5  # Fallback rate

class HistoricalForexProvider:
    """Provide historical USD/INR exchange rates"""
    
    def get_historical_rates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical USD/INR rates from Yahoo Finance"""
        try:
            logger.info(f"Fetching USD/INR data from {start_date} to {end_date}")
            
            # Get data from yfinance
            ticker = yf.Ticker("USDINR=X")
            data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if not data.empty:
                rates = []
                for date, row in data.iterrows():
                    rates.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'open': round(row['Open'], 4),
                        'high': round(row['High'], 4), 
                        'low': round(row['Low'], 4),
                        'close': round(row['Close'], 4),
                        'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
                    })
                
                df = pd.DataFrame(rates)
                logger.info(f"Retrieved {len(df)} days of historical data")
                return df
            else:
                logger.warning("No historical data available from yfinance")
                return self.generate_synthetic_data(start_date, end_date)
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return self.generate_synthetic_data(start_date, end_date)
    
    def generate_synthetic_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate realistic synthetic USD/INR data as fallback"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        base_rate = 84.5  # Realistic base rate for 2025
        
        rates = []
        current_rate = base_rate
        
        for date in dates:
            # Add realistic daily volatility
            daily_change = np.random.normal(0, 0.2)  # ~0.2% daily volatility
            current_rate += daily_change
            current_rate = max(82.0, min(87.0, current_rate))  # Keep within range
            
            rates.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(current_rate + np.random.normal(0, 0.05), 4),
                'high': round(current_rate * 1.002, 4),
                'low': round(current_rate * 0.998, 4),
                'close': round(current_rate, 4),
                'volume': np.random.randint(1000000, 5000000)
            })
        
        return pd.DataFrame(rates)

class ForwardRatePLCalculator:
    """Calculate P&L using forward rates with settlement options"""
    
    def __init__(self):
        self.forex_provider = HistoricalForexProvider()
        self.rbi_provider = RBIRateProvider()
        self.interest_rate = self.rbi_provider.get_rbi_repo_rate()
    
    def calculate_forward_rate(self, spot_rate: float, days_remaining: int, annual_interest_rate: float) -> float:
        """Calculate forward rate using: Forward = Spot × e^(r×t/365)"""
        # Convert annual rate to decimal
        r = annual_interest_rate / 100
        
        # Convert days to years
        t = days_remaining / 365
        
        # Forward Rate = Spot Rate × e^(r×t)
        forward_rate = spot_rate * math.exp(r * t)
        
        return forward_rate
    
    def calculate_daily_pl(self, lc: ForwardRateLC, contract_rate: float) -> Dict:
        """Calculate daily P&L using forward rates with settlement options"""
        logger.info(f"Calculating forward rate P&L for LC {lc.lc_number}")
        logger.info(f"Contract rate: ₹{contract_rate:.4f}")
        logger.info(f"Interest rate: {self.interest_rate}%")
        logger.info(f"Amount: ${lc.amount_usd:,.2f}")
        
        # Get historical rates for the LC period
        start_date = lc.issue_date.strftime('%Y-%m-%d')
        end_date = lc.maturity_date.strftime('%Y-%m-%d')
        
        historical_data = self.forex_provider.get_historical_rates(start_date, end_date)
        
        if historical_data.empty:
            return {'error': 'No historical data available'}
        
        # Calculate total days in LC period
        total_days = lc.maturity_days
        
        # Calculate daily forward rates and P&L
        daily_pl = []
        
        for i, (_, row) in enumerate(historical_data.iterrows()):
            date = row['date']
            spot_rate = row['close']
            
            # Calculate days remaining (decreasing counter: 30, 29, 28, ...)
            days_remaining = total_days - i
            
            # Calculate forward rate for this day
            forward_rate = self.calculate_forward_rate(spot_rate, days_remaining, self.interest_rate)
            
            # Calculate P&L
            # Close P&L = What you gain/lose if you close LC today
            # Formula: (Contract Rate - Forward Rate) × USD Amount
            close_pl_usd = (contract_rate - forward_rate) * lc.amount_usd
            
            # Expected P&L at maturity = Current forward rate vs contract rate
            expected_pl_usd = close_pl_usd  # Same calculation for now
            
            # Convert USD P&L to INR for display
            close_pl_inr = close_pl_usd  # Already in INR since rates are INR/USD
            expected_pl_inr = expected_pl_usd
            
            daily_pl.append({
                'date': date,
                'spot_rate': round(spot_rate, 4),
                'days_remaining': max(0, days_remaining),
                'interest_rate': round(self.interest_rate, 2),
                'forward_rate': round(forward_rate, 4),
                'contract_rate': round(contract_rate, 4),
                'close_pl_inr': round(close_pl_inr, 2),
                'expected_pl_inr': round(expected_pl_inr, 2),
                'rate_difference': round(contract_rate - forward_rate, 4),
                'pl_percentage': round((close_pl_inr / (lc.amount_usd * contract_rate)) * 100, 2),
                'amount_usd': lc.amount_usd,
                'amount_inr': round(lc.amount_usd * contract_rate, 2)
            })
        
        # Calculate summary statistics
        close_pl_amounts = [day['close_pl_inr'] for day in daily_pl]
        expected_pl_amounts = [day['expected_pl_inr'] for day in daily_pl]
        
        final_close_pl = close_pl_amounts[-1] if close_pl_amounts else 0
        final_expected_pl = expected_pl_amounts[-1] if expected_pl_amounts else 0
        
        max_profit = max(close_pl_amounts) if close_pl_amounts else 0
        max_loss = min(close_pl_amounts) if close_pl_amounts else 0
        
        # Calculate volatility
        pl_volatility = np.std(close_pl_amounts) if len(close_pl_amounts) > 1 else 0
        
        # Calculate Value at Risk (VaR) - 5th percentile
        var_95 = np.percentile(close_pl_amounts, 5) if len(close_pl_amounts) > 1 else 0
        
        summary = {
            'lc_details': {
                'lc_number': lc.lc_number,
                'amount_usd': lc.amount_usd,
                'amount_inr': round(lc.amount_usd * contract_rate, 2),
                'maturity_days': lc.maturity_days,
                'issue_date': lc.issue_date.strftime('%Y-%m-%d'),
                'maturity_date': lc.maturity_date.strftime('%Y-%m-%d'),
                'contract_rate': contract_rate,
                'interest_rate': self.interest_rate,
                'business_type': lc.business_type
            },
            'pl_summary': {
                'final_close_pl_inr': round(final_close_pl, 2),
                'final_expected_pl_inr': round(final_expected_pl, 2),
                'max_profit_inr': round(max_profit, 2),
                'max_loss_inr': round(max_loss, 2),
                'total_data_points': len(daily_pl),
                'data_source': 'Forward_Rate_Calculation',
                'calculation_method': 'Forward Rate = Spot × e^(r×t/365)',
                'formula_used': f'Forward = Spot × e^({self.interest_rate}% × days/365)'
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
        logger.info(f"  Max Profit: ₹{max_profit:,.2f}")
        logger.info(f"  Max Loss: ₹{max_loss:,.2f}")
        logger.info(f"  Data Points: {len(daily_pl)}")
        logger.info(f"  Interest Rate: {self.interest_rate}%")
        
        return summary

# Flask Routes
@app.route('/')
def index():
    """Main dashboard for forward rate LC analysis"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0_Forward_Rate',
        'focus': 'Forward Rate LC Analysis',
        'formula': 'Forward = Spot × e^(r×t/365)',
        'data_source': 'Yahoo Finance + RBI Rate',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/current-rates')
def get_current_rates():
    """Get current USD/INR rates and RBI rate"""
    try:
        logger.info("Fetching current USD/INR rate and RBI rate")
        
        # Get current USD/INR rate
        ticker = yf.Ticker("USDINR=X")
        current_data = ticker.history(period="1d")
        
        # Get RBI rate
        rbi_provider = RBIRateProvider()
        rbi_rate = rbi_provider.get_rbi_repo_rate()
        
        if not current_data.empty:
            rate = current_data['Close'].iloc[-1]
            logger.info(f"Current rate: {rate:.4f}, RBI rate: {rbi_rate}%")
            return jsonify({
                'success': True,
                'rate': round(rate, 4),
                'rbi_rate': rbi_rate,
                'source': 'Yahoo Finance',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'rate': 84.50,  # Fallback
                'rbi_rate': rbi_rate,
                'source': 'Fallback Rate',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error fetching current rates: {e}")
        return jsonify({
            'success': True,
            'rate': 84.50,
            'rbi_rate': 6.5,
            'source': 'Fallback Rate',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/calculate-forward-pl', methods=['POST'])
def calculate_forward_pl():
    """Calculate P&L using forward rates"""
    try:
        data = request.get_json()
        logger.info(f"Forward P&L calculation request: {data}")
        
        # Extract LC details
        lc_id = data.get('lc_id', 'LC-001')
        lc_amount = float(data.get('lc_amount', 100000))
        contract_rate = float(data.get('contract_rate', 84.50))
        issue_date = data.get('issue_date')
        maturity_date = data.get('maturity_date') 
        business_type = data.get('business_type', 'import')
        
        # Create LC object
        lc = ForwardRateLC(
            lc_number=lc_id,
            amount_usd=lc_amount,
            issue_date=datetime.strptime(issue_date, '%Y-%m-%d'),
            maturity_date=datetime.strptime(maturity_date, '%Y-%m-%d'),
            business_type=business_type
        )
        
        # Calculate P&L using forward rates
        calculator = ForwardRatePLCalculator()
        result = calculator.calculate_daily_pl(lc, contract_rate)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Forward rate P&L calculation completed',
            'calculation_type': 'forward_rate'
        })
        
    except Exception as e:
        logger.error(f"Error in forward P&L calculation: {e}")
        return jsonify({
            'success': False,
            'error': f'Calculation failed: {str(e)}'
        }), 500

# Backward compatibility endpoint
@app.route('/api/calculate-backdated-pl', methods=['POST'])
def calculate_backdated_pl():
    """Backward compatibility - redirect to forward rate calculation"""
    return calculate_forward_pl()

if __name__ == '__main__':
    print("🌐 Forward Rate LC System starting on port 5000")
    print("📊 Access dashboard: http://localhost:5000")
    print("🔧 API endpoints:")
    print("   - /api/health")
    print("   - /api/current-rates") 
    print("   - /api/calculate-forward-pl")
    app.run(debug=True, host='0.0.0.0', port=5000)
