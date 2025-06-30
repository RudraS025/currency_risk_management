"""
Profit and Loss calculator for currency risk management.
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
from ..models.letter_of_credit import LetterOfCredit
from ..data_providers.forex_provider import ForexDataProvider

logger = logging.getLogger(__name__)


class ProfitLossCalculator:
    """
    Calculates profit and loss for Letter of Credit transactions considering currency fluctuations.
    """
    
    def __init__(self, forex_provider: Optional[ForexDataProvider] = None):
        """
        Initialize the P&L calculator.
        
        Args:
            forex_provider: Forex data provider instance
        """
        self.forex_provider = forex_provider or ForexDataProvider()
    
    def calculate_current_pl(self, lc: LetterOfCredit, 
                           base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate current profit/loss for an LC transaction.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for P&L calculation (default: INR)
        
        Returns:
            Dictionary containing P&L calculations
        """
        try:
            # Get signing date exchange rate
            signing_rate = self._get_historical_rate_for_date(
                lc.currency, base_currency, lc.signing_date
            )
            
            # Get current exchange rate
            current_rate = self.forex_provider.get_current_rate(lc.currency, base_currency)
            
            if signing_rate is None or current_rate is None:
                logger.error(f"Could not retrieve exchange rates for {lc.currency}/{base_currency}")
                return self._empty_pl_result()
            
            # Calculate values in base currency
            lc_value_foreign = lc.total_value
            lc_value_base_at_signing = lc_value_foreign * signing_rate
            lc_value_base_current = lc_value_foreign * current_rate
            
            # Calculate P&L
            unrealized_pl = lc_value_base_current - lc_value_base_at_signing
            pl_percentage = (unrealized_pl / lc_value_base_at_signing) * 100
            
            # Calculate daily P&L if LC has been active for more than 0 days
            days_elapsed = max(lc.days_elapsed, 1)
            daily_pl = unrealized_pl / days_elapsed
            
            result = {
                'lc_id': lc.lc_id,
                'lc_value_foreign': lc_value_foreign,
                'lc_value_base_at_signing': lc_value_base_at_signing,
                'lc_value_base_current': lc_value_base_current,
                'signing_rate': signing_rate,
                'current_rate': current_rate,
                'unrealized_pl': unrealized_pl,
                'pl_percentage': pl_percentage,
                'daily_pl': daily_pl,
                'days_elapsed': days_elapsed,
                'days_remaining': lc.days_remaining,
                'foreign_currency': lc.currency,
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"Calculated P&L for {lc.lc_id}: {base_currency} {unrealized_pl:,.2f} ({pl_percentage:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating P&L for {lc.lc_id}: {e}")
            return self._empty_pl_result()
    
    def calculate_forward_pl_projection(self, lc: LetterOfCredit, 
                                      base_currency: str = "INR") -> Dict[str, float]:
        """
        Project P&L at LC maturity using forward rates.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for P&L calculation
        
        Returns:
            Dictionary containing forward P&L projections
        """
        try:
            # Get signing date exchange rate
            signing_rate = self._get_historical_rate_for_date(
                lc.currency, base_currency, lc.signing_date
            )
            
            # Get forward rate estimate for maturity date
            forward_rate = self.forex_provider.get_forward_rate_estimate(
                lc.currency, base_currency, lc.days_remaining
            )
            
            if signing_rate is None or forward_rate is None:
                logger.error(f"Could not retrieve rates for forward P&L projection")
                return self._empty_pl_result()
            
            # Calculate projected values
            lc_value_foreign = lc.total_value
            lc_value_base_at_signing = lc_value_foreign * signing_rate
            lc_value_base_at_maturity = lc_value_foreign * forward_rate
            
            # Calculate projected P&L
            projected_pl = lc_value_base_at_maturity - lc_value_base_at_signing
            projected_pl_percentage = (projected_pl / lc_value_base_at_signing) * 100
            
            result = {
                'lc_id': lc.lc_id,
                'lc_value_foreign': lc_value_foreign,
                'lc_value_base_at_signing': lc_value_base_at_signing,
                'lc_value_base_at_maturity': lc_value_base_at_maturity,
                'signing_rate': signing_rate,
                'forward_rate': forward_rate,
                'projected_pl': projected_pl,
                'projected_pl_percentage': projected_pl_percentage,
                'days_remaining': lc.days_remaining,
                'maturity_date': lc.maturity_date.strftime("%Y-%m-%d"),
                'foreign_currency': lc.currency,
                'base_currency': base_currency,
                'projection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"Projected P&L for {lc.lc_id} at maturity: {base_currency} {projected_pl:,.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating forward P&L projection for {lc.lc_id}: {e}")
            return self._empty_pl_result()
    
    def calculate_scenario_analysis(self, lc: LetterOfCredit, 
                                  rate_scenarios: List[float],
                                  base_currency: str = "INR") -> List[Dict[str, float]]:
        """
        Perform scenario analysis with different exchange rates.
        
        Args:
            lc: Letter of Credit instance
            rate_scenarios: List of exchange rates to analyze
            base_currency: Currency for P&L calculation
        
        Returns:
            List of P&L results for each scenario
        """
        try:
            signing_rate = self._get_historical_rate_for_date(
                lc.currency, base_currency, lc.signing_date
            )
            
            if signing_rate is None:
                logger.error("Could not retrieve signing date rate for scenario analysis")
                return []
            
            results = []
            lc_value_foreign = lc.total_value
            lc_value_base_at_signing = lc_value_foreign * signing_rate
            
            for i, scenario_rate in enumerate(rate_scenarios):
                lc_value_base_scenario = lc_value_foreign * scenario_rate
                scenario_pl = lc_value_base_scenario - lc_value_base_at_signing
                scenario_pl_percentage = (scenario_pl / lc_value_base_at_signing) * 100
                
                result = {
                    'scenario_id': i + 1,
                    'lc_id': lc.lc_id,
                    'scenario_rate': scenario_rate,
                    'signing_rate': signing_rate,
                    'rate_change_percentage': ((scenario_rate - signing_rate) / signing_rate) * 100,
                    'lc_value_base_at_signing': lc_value_base_at_signing,
                    'lc_value_base_scenario': lc_value_base_scenario,
                    'scenario_pl': scenario_pl,
                    'scenario_pl_percentage': scenario_pl_percentage,
                    'foreign_currency': lc.currency,
                    'base_currency': base_currency
                }
                
                results.append(result)
            
            logger.info(f"Completed scenario analysis for {lc.lc_id} with {len(rate_scenarios)} scenarios")
            return results
            
        except Exception as e:
            logger.error(f"Error in scenario analysis for {lc.lc_id}: {e}")
            return []
    
    def calculate_break_even_rate(self, lc: LetterOfCredit, 
                                base_currency: str = "INR") -> Optional[float]:
        """
        Calculate the break-even exchange rate (same as signing rate).
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for calculation
        
        Returns:
            Break-even exchange rate
        """
        try:
            break_even_rate = self._get_historical_rate_for_date(
                lc.currency, base_currency, lc.signing_date
            )
            
            if break_even_rate is not None:
                logger.info(f"Break-even rate for {lc.lc_id}: {break_even_rate}")
            
            return break_even_rate
            
        except Exception as e:
            logger.error(f"Error calculating break-even rate for {lc.lc_id}: {e}")
            return None
    
    def calculate_portfolio_pl(self, lcs: List[LetterOfCredit], 
                             base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate combined P&L for a portfolio of LCs.
        
        Args:
            lcs: List of Letter of Credit instances
            base_currency: Currency for P&L calculation
        
        Returns:
            Combined portfolio P&L metrics
        """
        try:
            total_value_at_signing = 0.0
            total_value_current = 0.0
            total_unrealized_pl = 0.0
            successful_calculations = 0
            
            lc_details = []
            
            for lc in lcs:
                lc_pl = self.calculate_current_pl(lc, base_currency)
                
                if lc_pl.get('lc_value_base_at_signing'):  # Valid calculation
                    total_value_at_signing += lc_pl['lc_value_base_at_signing']
                    total_value_current += lc_pl['lc_value_base_current']
                    total_unrealized_pl += lc_pl['unrealized_pl']
                    successful_calculations += 1
                    
                    lc_details.append({
                        'lc_id': lc.lc_id,
                        'unrealized_pl': lc_pl['unrealized_pl'],
                        'pl_percentage': lc_pl['pl_percentage']
                    })
            
            if successful_calculations == 0:
                return self._empty_portfolio_result()
            
            portfolio_pl_percentage = (total_unrealized_pl / total_value_at_signing) * 100 if total_value_at_signing > 0 else 0
            
            result = {
                'total_lcs': len(lcs),
                'successful_calculations': successful_calculations,
                'total_value_at_signing': total_value_at_signing,
                'total_value_current': total_value_current,
                'total_unrealized_pl': total_unrealized_pl,
                'portfolio_pl_percentage': portfolio_pl_percentage,
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'lc_details': lc_details
            }
            
            logger.info(f"Portfolio P&L calculated: {base_currency} {total_unrealized_pl:,.2f} ({portfolio_pl_percentage:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating portfolio P&L: {e}")
            return self._empty_portfolio_result()
    
    def _get_historical_rate_for_date(self, from_currency: str, to_currency: str, 
                                    date_str: str) -> Optional[float]:
        """Get historical exchange rate for a specific date."""
        try:
            # Try to get exact date first
            historical_rates = self.forex_provider.get_historical_rates(
                from_currency, to_currency, date_str, date_str
            )
            
            if historical_rates and date_str in historical_rates:
                return historical_rates[date_str]
            
            # If exact date not available, try a range around the date
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = (date_obj - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (date_obj + timedelta(days=5)).strftime("%Y-%m-%d")
            
            historical_rates = self.forex_provider.get_historical_rates(
                from_currency, to_currency, start_date, end_date
            )
            
            if historical_rates:
                # Find the closest date
                closest_date = min(historical_rates.keys(), 
                                 key=lambda d: abs((datetime.strptime(d, "%Y-%m-%d") - date_obj).days))
                return historical_rates[closest_date]
            
            logger.warning(f"No historical rate found for {from_currency}/{to_currency} around {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving historical rate for {date_str}: {e}")
            return None
    
    def _empty_pl_result(self) -> Dict[str, float]:
        """Return empty P&L result structure."""
        return {
            'lc_id': '',
            'lc_value_foreign': 0.0,
            'lc_value_base_at_signing': 0.0,
            'lc_value_base_current': 0.0,
            'signing_rate': 0.0,
            'current_rate': 0.0,
            'unrealized_pl': 0.0,
            'pl_percentage': 0.0,
            'daily_pl': 0.0,
            'days_elapsed': 0,
            'days_remaining': 0,
            'foreign_currency': '',
            'base_currency': '',
            'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _empty_portfolio_result(self) -> Dict[str, float]:
        """Return empty portfolio result structure."""
        return {
            'total_lcs': 0,
            'successful_calculations': 0,
            'total_value_at_signing': 0.0,
            'total_value_current': 0.0,
            'total_unrealized_pl': 0.0,
            'portfolio_pl_percentage': 0.0,
            'base_currency': '',
            'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'lc_details': []
        }
