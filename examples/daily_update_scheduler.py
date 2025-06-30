"""
Daily Update Scheduler for Currency Risk Management System
Handles automated updates, alerts, and maintenance tasks
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import schedule
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currency_risk_mgmt.data_providers.forex_provider import ForexDataProvider
from currency_risk_mgmt.data_providers.forward_rates_provider import ForwardRatesProvider
from currency_risk_mgmt.models.letter_of_credit import LetterOfCredit
from currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator
from currency_risk_mgmt.calculators.risk_metrics import RiskMetricsCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_updates.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DailyUpdateScheduler:
    """Handles daily automated tasks"""
    
    def __init__(self):
        self.forex_provider = ForexDataProvider()
        self.forward_provider = ForwardRatesProvider()
        self.pl_calculator = ForwardPLCalculator()
        self.risk_calculator = RiskMetricsCalculator()
        
    def update_exchange_rates(self):
        """Update and cache latest exchange rates"""
        try:
            logger.info("Starting daily exchange rate update...")
            
            # Update spot rates
            current_rate = self.forex_provider.get_current_rate('USD', 'INR')
            logger.info(f"Current USD/INR rate: {current_rate}")
            
            # Update forward rates for standard periods
            forward_rates = {}
            periods = [30, 60, 90, 180, 365]
            
            for days in periods:
                maturity_date = datetime.now() + timedelta(days=days)
                forward_curve = self.forward_provider.get_forward_curve('USD', 'INR', datetime.now().strftime('%Y-%m-%d'))
                rate = forward_curve.get(f'{days}d', 85.0)  # Default fallback
                forward_rates[f'{days}d'] = rate
                logger.info(f"Forward rate {days}d: {rate}")
            
            # Save rates to file for dashboard
            rates_data = {
                'timestamp': datetime.now().isoformat(),
                'spot_rate': current_rate,
                'forward_rates': forward_rates
            }
            
            with open('daily_rates.json', 'w') as f:
                json.dump(rates_data, f, indent=2)
            
            logger.info("Exchange rates updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating exchange rates: {str(e)}")
    
    def check_alerts(self):
        """Check for rate alerts and risk thresholds"""
        try:
            logger.info("Checking for alerts...")
            
            # Load current rates
            with open('daily_rates.json', 'r') as f:
                rates_data = json.load(f)
            
            current_rate = rates_data['spot_rate']
            
            # Example alert thresholds (can be configured)
            alert_thresholds = {
                'high_volatility': 0.02,  # 2% daily change
                'rate_threshold_high': 85.0,
                'rate_threshold_low': 80.0
            }
            
            alerts = []
            
            # Check rate thresholds
            if current_rate > alert_thresholds['rate_threshold_high']:
                alerts.append(f"HIGH ALERT: USD/INR rate ({current_rate}) above threshold ({alert_thresholds['rate_threshold_high']})")
            elif current_rate < alert_thresholds['rate_threshold_low']:
                alerts.append(f"LOW ALERT: USD/INR rate ({current_rate}) below threshold ({alert_thresholds['rate_threshold_low']})")
            
            # Log alerts
            for alert in alerts:
                logger.warning(alert)
            
            if not alerts:
                logger.info("No alerts triggered")
                
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
    
    def generate_daily_summary(self):
        """Generate daily market summary"""
        try:
            logger.info("Generating daily market summary...")
            
            # Create a sample LC for analysis
            sample_lc = LetterOfCredit(
                lc_id="DAILY-SAMPLE-001",
                commodity="Sample Export",
                quantity=1000,
                unit="tons",
                rate_per_unit=100,
                currency="USD",
                signing_date=datetime.now().strftime('%Y-%m-%d'),
                maturity_days=90,
                customer_country="Sample Country"
            )
            
            # Calculate P&L and risk metrics
            pl_result = self.pl_calculator.calculate_daily_forward_pl(sample_lc, 'INR')
            risk_metrics = self.risk_calculator.calculate_value_at_risk(sample_lc, base_currency='INR')
            
            summary = {
                'date': datetime.now().isoformat(),
                'sample_analysis': {
                    'lc_amount_usd': 100000,
                    'pl_result': pl_result,
                    'risk_metrics': risk_metrics
                }
            }
            
            # Save summary
            with open(f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info("Daily summary generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}")
    
    def cleanup_old_files(self):
        """Clean up old log and data files"""
        try:
            logger.info("Cleaning up old files...")
            
            # Delete files older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for filename in os.listdir('.'):
                if filename.startswith('daily_summary_') and filename.endswith('.json'):
                    file_date_str = filename.replace('daily_summary_', '').replace('.json', '')
                    try:
                        file_date = datetime.strptime(file_date_str, '%Y%m%d')
                        if file_date < cutoff_date:
                            os.remove(filename)
                            logger.info(f"Deleted old file: {filename}")
                    except ValueError:
                        continue
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def run_daily_tasks(self):
        """Run all daily maintenance tasks"""
        logger.info("=== Starting Daily Tasks ===")
        
        self.update_exchange_rates()
        self.check_alerts()
        self.generate_daily_summary()
        self.cleanup_old_files()
        
        logger.info("=== Daily Tasks Completed ===")

def main():
    """Main scheduler function"""
    scheduler = DailyUpdateScheduler()
    
    # Schedule daily tasks
    schedule.every().day.at("09:00").do(scheduler.run_daily_tasks)
    schedule.every().day.at("15:00").do(scheduler.update_exchange_rates)
    schedule.every().day.at("21:00").do(scheduler.check_alerts)
    
    logger.info("Daily scheduler started. Waiting for scheduled tasks...")
    
    # For Heroku, run tasks immediately on startup
    if os.environ.get('DYNO'):
        logger.info("Running on Heroku - executing initial tasks")
        scheduler.run_daily_tasks()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
