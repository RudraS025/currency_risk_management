"""
Enhanced Profit and Loss calculator with Forward Rates support.
Calculates P&L based on daily forward rates for LC maturity date.
"""

from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
from ..models.letter_of_credit import LetterOfCredit
from ..data_providers.forward_rates_provider import ForwardRatesProvider, ForwardRate
from ..data_providers.forex_provider import ForexDataProvider

logger = logging.getLogger(__name__)


class ForwardPLCalculator:
    """
    Calculates P&L based on forward rates for LC maturity date.
    This shows how your LC value changes based on forward market expectations.
    """
    
    def __init__(self, forward_provider: Optional[ForwardRatesProvider] = None,
                 forex_provider: Optional[ForexDataProvider] = None):
        """
        Initialize the Forward P&L calculator.
        
        Args:
            forward_provider: Forward rates provider instance  
            forex_provider: Forex data provider instance
        """
        self.forward_provider = forward_provider or ForwardRatesProvider()
        self.forex_provider = forex_provider or ForexDataProvider()
    
    def calculate_daily_forward_pl(self, lc: LetterOfCredit, 
                                  base_currency: str = "INR") -> Dict[str, Any]:
        """
        Calculate daily P&L based on forward rates from signing to maturity.
        
        This shows how the expected value at maturity changes each day
        based on forward market rates.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for P&L calculation
        
        Returns:
            Dictionary with daily P&L based on forward rates, including summary statistics
        """
        try:
            logger.info(f"Calculating daily forward P&L for {lc.lc_id}")
            
            # Generate daily dates from signing to today (or maturity if past)
            start_date = datetime.strptime(lc.signing_date, "%Y-%m-%d")
            end_date = min(datetime.now(), lc.maturity_date)
            
            daily_dates = []
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends for business days only
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    daily_dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            if not daily_dates:
                logger.error("No valid business dates found")
                return {}
            
            # Calculate forward rates for each day
            daily_forward_rates = {}
            maturity_date_str = lc.maturity_date.strftime("%Y-%m-%d")
            
            for date_str in daily_dates:
                # Calculate days to maturity from this date
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
                days_to_maturity = (lc.maturity_date - current_date).days
                
                if days_to_maturity >= 0:
                    forward_rate = self.forward_provider.get_forward_rate(
                        lc.currency, base_currency, date_str, maturity_date_str
                    )
                    
                    if forward_rate:
                        daily_forward_rates[date_str] = forward_rate.rate
            
            if not daily_forward_rates:
                logger.error("No forward rates available")
                return {}
            
            # Get initial forward rate (at signing)
            signing_date_str = lc.signing_date
            signing_forward_rate = daily_forward_rates.get(signing_date_str)
            
            if signing_forward_rate is None:
                # Use the first available rate
                signing_forward_rate = next(iter(daily_forward_rates.values()))
            
            # Calculate daily P&L
            daily_pl_data = {}
            daily_pl_values = []
            previous_value = lc.total_value * signing_forward_rate
            
            for date_str in sorted(daily_forward_rates.keys()):
                forward_rate = daily_forward_rates[date_str]
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
                days_to_maturity = (lc.maturity_date - current_date).days
                
                # Current expected value at maturity
                current_expected_value = lc.total_value * forward_rate
                
                # P&L vs initial expectation
                unrealized_pl = current_expected_value - (lc.total_value * signing_forward_rate)
                pl_percentage = (unrealized_pl / (lc.total_value * signing_forward_rate)) * 100
                
                # Daily change
                daily_change = current_expected_value - previous_value
                
                daily_pl_data[date_str] = {
                    'date': date_str,
                    'forward_rate': forward_rate,
                    'days_to_maturity': days_to_maturity,
                    'expected_value_at_maturity': current_expected_value,
                    'unrealized_pl': unrealized_pl,
                    'pl_percentage': pl_percentage,
                    'daily_change': daily_change,
                    'cumulative_pl': unrealized_pl
                }
                
                daily_pl_values.append(unrealized_pl)
                previous_value = current_expected_value
            
            # Calculate summary statistics
            if daily_pl_values:
                max_pl = max(daily_pl_values)
                min_pl = min(daily_pl_values)
                avg_pl = sum(daily_pl_values) / len(daily_pl_values)
                current_pl = daily_pl_values[-1] if daily_pl_values else 0
                
                # Find max profit and loss dates
                max_pl_date = None
                min_pl_date = None
                for date_str, data in daily_pl_data.items():
                    if data['unrealized_pl'] == max_pl:
                        max_pl_date = date_str
                    if data['unrealized_pl'] == min_pl:
                        min_pl_date = date_str
            else:
                max_pl = min_pl = avg_pl = current_pl = 0
                max_pl_date = min_pl_date = None
            
            # Prepare result with all data needed for visualization
            result = {
                'lc_id': lc.lc_id,
                'currency_pair': f"{lc.currency}/{base_currency}",
                'lc_amount': lc.total_value,
                'signing_date': signing_date_str,
                'maturity_date': maturity_date_str,
                'signing_forward_rate': signing_forward_rate,
                'current_forward_rate': daily_forward_rates.get(sorted(daily_forward_rates.keys())[-1], signing_forward_rate),
                'daily_pl': daily_pl_data,
                'summary': {
                    'current_pl': current_pl,
                    'max_profit': max_pl,
                    'max_loss': min_pl,
                    'avg_pl': avg_pl,
                    'max_profit_date': max_pl_date,
                    'max_loss_date': min_pl_date,
                    'total_days': len(daily_pl_data),
                    'volatility': np.std(daily_pl_values) if len(daily_pl_values) > 1 else 0
                },
                'chart_data': [
                    {'date': date_str, 'pl': data['unrealized_pl']} 
                    for date_str, data in daily_pl_data.items()
                ]
            }
            
            logger.info(f"Calculated daily P&L for {len(daily_pl_data)} days. Current P&L: {current_pl:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating daily forward P&L: {e}")
            return {}
    
    def calculate_exit_scenario_pl(self, lc: LetterOfCredit,
                                  exit_date: str,
                                  base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate P&L if exiting LC position on a specific date.
        
        Args:
            lc: Letter of Credit instance
            exit_date: Date of exit (YYYY-MM-DD)
            base_currency: Currency for P&L calculation
        
        Returns:  
            Dictionary with exit scenario P&L
        """
        try:
            logger.info(f"Calculating exit scenario P&L for {exit_date}")
            
            # Get spot rate on exit date
            exit_spot_rate = self._get_spot_rate_for_date(
                lc.currency, base_currency, exit_date
            )
            
            # Get original forward rate at signing
            signing_forward_rate = self._get_signing_forward_rate(lc, base_currency)
            
            if not exit_spot_rate or not signing_forward_rate:
                return {}
            
            # Calculate exit values
            original_expected_value = lc.total_value * signing_forward_rate
            exit_value = lc.total_value * exit_spot_rate
            
            # Calculate P&L
            unrealized_pl = exit_value - original_expected_value
            pl_percentage = (unrealized_pl / original_expected_value) * 100
            
            # Days held
            exit_dt = datetime.strptime(exit_date, "%Y-%m-%d")
            signing_dt = datetime.strptime(lc.signing_date, "%Y-%m-%d")
            days_held = (exit_dt - signing_dt).days
            
            return {
                'exit_date': exit_date,
                'days_held': days_held,
                'exit_spot_rate': exit_spot_rate,
                'signing_forward_rate': signing_forward_rate,
                'original_expected_value': original_expected_value,
                'exit_value': exit_value,
                'unrealized_pl': unrealized_pl,
                'pl_percentage': pl_percentage,
                'daily_pl': unrealized_pl / max(days_held, 1),
                'scenario': 'early_exit'
            }
            
        except Exception as e:
            logger.error(f"Error calculating exit scenario P&L: {e}")
            return {}
    
    def calculate_hold_to_maturity_pl(self, lc: LetterOfCredit,
                                     base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate P&L if holding LC to maturity.
        Uses current forward rate for maturity date.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for P&L calculation
        
        Returns:
            Dictionary with hold-to-maturity P&L
        """
        try:
            logger.info("Calculating hold-to-maturity P&L")
            
            # Get current forward rate for maturity
            current_forward_rate = self.forward_provider.estimate_forward_rate(
                lc.currency, base_currency, lc.days_remaining
            )
            
            # Get original forward rate at signing
            signing_forward_rate = self._get_signing_forward_rate(lc, base_currency)
            
            if not current_forward_rate or not signing_forward_rate:
                return {}
            
            # Calculate maturity values
            original_expected_value = lc.total_value * signing_forward_rate
            current_expected_value = lc.total_value * current_forward_rate
            
            # Calculate P&L
            unrealized_pl = current_expected_value - original_expected_value
            pl_percentage = (unrealized_pl / original_expected_value) * 100
            
            return {
                'maturity_date': lc.maturity_date.strftime("%Y-%m-%d"),
                'days_remaining': lc.days_remaining,
                'current_forward_rate': current_forward_rate,
                'signing_forward_rate': signing_forward_rate,
                'original_expected_value': original_expected_value,
                'current_expected_value': current_expected_value,
                'unrealized_pl': unrealized_pl,
                'pl_percentage': pl_percentage,
                'scenario': 'hold_to_maturity'
            }
            
        except Exception as e:
            logger.error(f"Error calculating hold-to-maturity P&L: {e}")
            return {}
    
    def generate_forward_pl_report(self, lc: LetterOfCredit,
                                  base_currency: str = "INR") -> Dict[str, any]:
        """
        Generate comprehensive forward P&L report.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for calculations
        
        Returns:
            Complete forward P&L analysis report
        """
        try:
            logger.info(f"Generating forward P&L report for {lc.lc_id}")
            
            # Get daily forward P&L
            daily_forward_pl = self.calculate_daily_forward_pl(lc, base_currency)
            
            # Calculate scenarios
            hold_to_maturity = self.calculate_hold_to_maturity_pl(lc, base_currency)
            
            # Calculate exit scenarios for different dates
            exit_scenarios = []
            
            # Exit scenarios: 7 days, 30 days, 60 days from now
            for days_ahead in [7, 30, 60]:
                if days_ahead < lc.days_remaining:
                    exit_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                    exit_scenario = self.calculate_exit_scenario_pl(lc, exit_date, base_currency)
                    if exit_scenario:
                        exit_scenarios.append(exit_scenario)
            
            # Get current status
            current_status = self._get_current_forward_status(daily_forward_pl)
            
            # Create summary
            report = {
                'lc_details': {
                    'lc_id': lc.lc_id,
                    'commodity': lc.commodity,
                    'total_value': lc.total_value,
                    'currency': lc.currency,
                    'signing_date': lc.signing_date,
                    'maturity_date': lc.maturity_date.strftime("%Y-%m-%d"),
                    'days_remaining': lc.days_remaining
                },
                'current_status': current_status,
                'daily_forward_pl': daily_forward_pl,
                'hold_to_maturity_scenario': hold_to_maturity,
                'exit_scenarios': exit_scenarios,
                'analysis': {
                    'total_days_tracked': len(daily_forward_pl),
                    'forward_rate_trend': self._analyze_forward_trend(daily_forward_pl),
                    'volatility': self._calculate_forward_volatility(daily_forward_pl),
                    'recommendation': self._generate_recommendation(daily_forward_pl, hold_to_maturity, exit_scenarios)
                },
                'report_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'base_currency': base_currency
            }
            
            logger.info("Forward P&L report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating forward P&L report: {e}")
            return {}
    
    def calculate_scenario_analysis(self, lc: LetterOfCredit, rate_change: float = 0.0) -> Dict[str, Any]:
        """
        Calculate scenario analysis for different rate changes.
        
        Args:
            lc: Letter of Credit instance
            rate_change: Rate change as decimal (e.g., 0.05 for 5% increase)
        
        Returns:
            Dictionary with scenario analysis results
        """
        try:
            logger.info(f"Calculating scenario analysis with {rate_change:.2%} rate change")
            
            # Get current forward rate
            current_forward_rate = self.forward_provider.estimate_forward_rate(
                lc.currency, 'INR', lc.days_remaining
            )
            
            if not current_forward_rate:
                current_forward_rate = 85.0  # Fallback rate
            
            # Apply scenario rate change
            scenario_rate = current_forward_rate * (1 + rate_change)
            
            # Calculate total value in USD
            total_value_usd = lc.total_value
            
            # Calculate scenario P&L
            current_value_inr = total_value_usd * current_forward_rate
            scenario_value_inr = total_value_usd * scenario_rate
            scenario_pl = scenario_value_inr - current_value_inr
            
            # Determine impact level
            if abs(rate_change) < 0.02:
                impact = "Low Impact"
            elif abs(rate_change) < 0.05:
                impact = "Medium Impact"
            else:
                impact = "High Impact"
            
            return {
                'scenario_rate': scenario_rate,
                'current_rate': current_forward_rate,
                'rate_change_percent': rate_change * 100,
                'total_pl_inr': scenario_pl,
                'current_value_inr': current_value_inr,
                'scenario_value_inr': scenario_value_inr,
                'impact': impact,
                'recommendation': 'Monitor' if abs(rate_change) < 0.02 else 'Consider hedging'
            }
            
        except Exception as e:
            logger.error(f"Error calculating scenario analysis: {e}")
            return {
                'total_pl_inr': 0,
                'impact': 'Error in calculation',
                'scenario_rate': 85.0,
                'current_rate': 85.0,
                'rate_change_percent': rate_change * 100
            }
    
    def _get_signing_forward_rate(self, lc: LetterOfCredit, base_currency: str) -> Optional[float]:
        """Get forward rate that was available at signing date for the maturity."""
        try:
            days_to_maturity_at_signing = (lc.maturity_date - lc.signing_date_obj).days
            
            forward_rate_obj = self.forward_provider._get_forward_rate_for_date(
                lc.currency, base_currency, lc.signing_date,
                lc.maturity_date.strftime("%Y-%m-%d"), days_to_maturity_at_signing
            )
            
            return forward_rate_obj.rate if forward_rate_obj else None
            
        except Exception as e:
            logger.error(f"Error getting signing forward rate: {e}")
            return None
    
    def _get_spot_rate_for_date(self, base_currency: str, quote_currency: str, date: str) -> Optional[float]:
        """Get spot rate for a specific date."""
        try:
            # Try to get historical spot rate
            historical_rates = self.forex_provider.get_historical_rates(
                base_currency, quote_currency, date, date
            )
            
            if historical_rates and date in historical_rates:
                return historical_rates[date]
            
            # Fallback to current rate if historical not available
            return self.forex_provider.get_current_rate(base_currency, quote_currency)
            
        except Exception as e:
            logger.error(f"Error getting spot rate for {date}: {e}")
            return None
    
    def _get_current_forward_status(self, daily_forward_pl: Dict) -> Dict:
        """Get current forward P&L status."""
        if not daily_forward_pl:
            return {}
        
        # Get latest date
        latest_date = max(daily_forward_pl.keys())
        latest_data = daily_forward_pl[latest_date]
        
        return {
            'current_date': latest_date,
            'current_forward_rate': latest_data['forward_rate'],
            'expected_value_at_maturity': latest_data['expected_value_at_maturity'],
            'unrealized_pl': latest_data['unrealized_pl'],
            'pl_percentage': latest_data['pl_percentage'],
            'days_to_maturity': latest_data['days_to_maturity']
        }
    
    def _analyze_forward_trend(self, daily_forward_pl: Dict) -> str:
        """Analyze trend in forward rates."""
        if len(daily_forward_pl) < 2:
            return "insufficient_data"
        
        rates = [data['forward_rate'] for data in daily_forward_pl.values()]
        
        # Simple trend analysis
        if rates[-1] > rates[0]:
            return "strengthening"
        elif rates[-1] < rates[0]:
            return "weakening"
        else:
            return "stable"
    
    def _calculate_forward_volatility(self, daily_forward_pl: Dict) -> float:
        """Calculate volatility of forward rates."""
        if len(daily_forward_pl) < 2:
            return 0.0
        
        rates = [data['forward_rate'] for data in daily_forward_pl.values()]
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(rates)):
            returns.append((rates[i] - rates[i-1]) / rates[i-1])
        
        # Return standard deviation
        if returns:
            return float(pd.Series(returns).std())
        return 0.0
    
    def _generate_recommendation(self, daily_pl: Dict, hold_scenario: Dict, exit_scenarios: List) -> str:
        """Generate recommendation based on forward analysis."""
        try:
            if not daily_pl or not hold_scenario:
                return "insufficient_data"
            
            current_pl = self._get_current_forward_status(daily_pl)
            
            # Simple recommendation logic
            if current_pl.get('pl_percentage', 0) > 2:
                return "consider_locking_gains"
            elif current_pl.get('pl_percentage', 0) < -3:
                return "consider_exit_or_hedge"
            elif hold_scenario.get('pl_percentage', 0) > current_pl.get('pl_percentage', 0):
                return "hold_position"
            else:
                return "monitor_closely"
                
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "error_in_analysis"
