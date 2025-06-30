"""
Forward Rates Data Provider for Currency Risk Management.
Provides forward exchange rates for different maturity periods.
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import requests
import logging
import numpy as np
from dataclasses import dataclass
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ForwardRate:
    """Represents a forward exchange rate quote"""
    date: str  # Quote date
    maturity_date: str  # Settlement/maturity date
    rate: float  # Forward rate
    days_to_maturity: int  # Days until maturity
    source: str  # Data source
    confidence: float = 1.0  # Confidence score


class ForwardRatesProvider:
    """
    Provides forward exchange rates for currency pairs.
    Uses multiple sources and calculations to estimate forward rates.
    """
    
    def __init__(self):
        """Initialize the forward rates provider."""
        self.sources = {
            'calculated': self._calculate_forward_rates,
            'market_data': self._fetch_market_forward_rates,
            'interest_rate_parity': self._calculate_irp_forward_rates
        }
    
    def get_daily_forward_rates(self, base_currency: str, quote_currency: str,
                               maturity_date: str, start_date: str,
                               end_date: Optional[str] = None) -> Dict[str, ForwardRate]:
        """
        Get daily forward rates for a specific maturity date.
        
        Args:
            base_currency: Base currency (e.g., 'USD')
            quote_currency: Quote currency (e.g., 'INR')
            maturity_date: Target maturity date (YYYY-MM-DD)
            start_date: Start date for forward rate series (YYYY-MM-DD)
            end_date: End date for forward rate series (default: today)
        
        Returns:
            Dictionary with date as key and ForwardRate as value
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"Fetching forward rates for {base_currency}/{quote_currency} "
                       f"maturing {maturity_date} from {start_date} to {end_date}")
            
            forward_rates = {}
            
            # Generate date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            maturity_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
            
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime("%Y-%m-%d")
                days_to_maturity = (maturity_dt - current_dt).days
                
                if days_to_maturity >= 0:  # Only if maturity is in future
                    forward_rate = self._get_forward_rate_for_date(
                        base_currency, quote_currency, date_str, 
                        maturity_date, days_to_maturity
                    )
                    
                    if forward_rate:
                        forward_rates[date_str] = forward_rate
                
                current_dt += timedelta(days=1)
            
            logger.info(f"Retrieved {len(forward_rates)} forward rate quotes")
            return forward_rates
            
        except Exception as e:
            logger.error(f"Error fetching daily forward rates: {e}")
            return {}
    
    def _get_forward_rate_for_date(self, base_currency: str, quote_currency: str,
                                  quote_date: str, maturity_date: str,
                                  days_to_maturity: int) -> Optional[ForwardRate]:
        """Get forward rate for a specific date."""
        try:
            # Try different methods in order of preference
            methods = [
                'calculated',
                'interest_rate_parity',
                'market_data'
            ]
            
            for method in methods:
                try:
                    rate = self.sources[method](
                        base_currency, quote_currency, quote_date, days_to_maturity
                    )
                    
                    if rate:
                        return ForwardRate(
                            date=quote_date,
                            maturity_date=maturity_date,
                            rate=rate,
                            days_to_maturity=days_to_maturity,
                            source=method,
                            confidence=0.8 if method == 'calculated' else 0.6
                        )
                        
                except Exception as e:
                    logger.debug(f"Method {method} failed: {e}")
                    continue
            
            logger.warning(f"No forward rate available for {quote_date}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting forward rate for {quote_date}: {e}")
            return None
    
    def _calculate_forward_rates(self, base_currency: str, quote_currency: str,
                               quote_date: str, days_to_maturity: int) -> Optional[float]:
        """
        Calculate forward rates using spot rate and estimated volatility.
        This is a simplified model for demonstration.
        """
        try:
            # Get historical spot rates around the quote date
            pair_symbol = f"{base_currency}{quote_currency}=X"
            
            # Get data from a few days before to a few days after quote_date
            start_date = (datetime.strptime(quote_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = (datetime.strptime(quote_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
            
            ticker = yf.Ticker(pair_symbol)
            hist_data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if hist_data.empty:
                return None
            
            # Get spot rate closest to quote date
            quote_dt = datetime.strptime(quote_date, "%Y-%m-%d")
            closest_date = min(hist_data.index, 
                             key=lambda x: abs((x.date() - quote_dt.date()).days))
            spot_rate = hist_data.loc[closest_date, 'Close']
            
            # Calculate volatility from recent history
            returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1)).dropna()
            daily_vol = returns.std()
            
            # Simple forward rate calculation (spot + drift + volatility adjustment)
            # This is a simplified model - in reality, you'd use interest rate differentials
            time_factor = days_to_maturity / 365.0
            
            # Add a small drift based on recent trend
            recent_returns = returns.tail(5).mean() if len(returns) >= 5 else 0
            drift = recent_returns * time_factor
            
            # Volatility adjustment (simplified)
            vol_adjustment = daily_vol * np.sqrt(time_factor) * np.random.normal(0, 0.1)
            
            forward_rate = spot_rate * (1 + drift + vol_adjustment)
            
            logger.debug(f"Calculated forward rate: {forward_rate:.4f} for {days_to_maturity} days")
            return float(forward_rate)
            
        except Exception as e:
            logger.error(f"Error calculating forward rate: {e}")
            return None
    
    def _calculate_irp_forward_rates(self, base_currency: str, quote_currency: str,
                                   quote_date: str, days_to_maturity: int) -> Optional[float]:
        """
        Calculate forward rates using Interest Rate Parity (IRP).
        F = S × (1 + r_quote × t) / (1 + r_base × t)
        """
        try:
            # Get spot rate
            pair_symbol = f"{base_currency}{quote_currency}=X"
            ticker = yf.Ticker(pair_symbol)
            
            # Get spot rate for the quote date
            start_date = (datetime.strptime(quote_date, "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
            end_date = (datetime.strptime(quote_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
            
            hist_data = ticker.history(start=start_date, end=end_date, interval="1d")
            if hist_data.empty:
                return None
            
            spot_rate = hist_data['Close'].iloc[-1]
            
            # Use estimated interest rates (in real implementation, get from treasury/RBI data)
            interest_rates = {
                'USD': 0.05,  # 5% annual
                'INR': 0.065,  # 6.5% annual
                'EUR': 0.03,   # 3% annual
                'GBP': 0.045   # 4.5% annual
            }
            
            base_rate = interest_rates.get(base_currency, 0.04)
            quote_rate = interest_rates.get(quote_currency, 0.05)
            
            # Calculate forward rate using IRP
            time_factor = days_to_maturity / 365.0
            forward_rate = spot_rate * (1 + quote_rate * time_factor) / (1 + base_rate * time_factor)
            
            logger.debug(f"IRP forward rate: {forward_rate:.4f}")
            return float(forward_rate)
            
        except Exception as e:
            logger.error(f"Error calculating IRP forward rate: {e}")
            return None
    
    def _fetch_market_forward_rates(self, base_currency: str, quote_currency: str,
                                  quote_date: str, days_to_maturity: int) -> Optional[float]:
        """
        Fetch forward rates from market data providers.
        In a real implementation, this would connect to Bloomberg, Reuters, etc.
        """
        try:
            # Placeholder for market data API calls
            # In reality, you would connect to:
            # - Bloomberg API
            # - Reuters Eikon
            # - Banks' FX API
            # - Central Bank data
            
            logger.debug("Market forward rates not implemented - using calculated rates")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market forward rates: {e}")
            return None
    
    def get_forward_curve(self, base_currency: str, quote_currency: str,
                         quote_date: str, max_days: int = 365) -> Dict[int, float]:
        """
        Get forward curve (forward rates for different maturities).
        
        Args:
            base_currency: Base currency
            quote_currency: Quote currency
            quote_date: Quote date
            max_days: Maximum days for forward curve
        
        Returns:
            Dictionary with days as key and forward rate as value
        """
        try:
            forward_curve = {}
            
            # Get forward rates for different maturities
            maturity_days = [1, 7, 30, 60, 90, 180, 270, 365]
            maturity_days = [d for d in maturity_days if d <= max_days]
            
            for days in maturity_days:
                maturity_date = (datetime.strptime(quote_date, "%Y-%m-%d") + 
                               timedelta(days=days)).strftime("%Y-%m-%d")
                
                forward_rate = self._get_forward_rate_for_date(
                    base_currency, quote_currency, quote_date, maturity_date, days
                )
                
                if forward_rate:
                    forward_curve[days] = forward_rate.rate
            
            return forward_curve
            
        except Exception as e:
            logger.error(f"Error getting forward curve: {e}")
            return {}
    
    def estimate_forward_rate(self, base_currency: str, quote_currency: str,
                            days_ahead: int) -> Optional[float]:
        """
        Estimate forward rate for a specific number of days ahead.
        
        Args:
            base_currency: Base currency
            quote_currency: Quote currency  
            days_ahead: Days until maturity
        
        Returns:
            Estimated forward rate
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            maturity_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            
            forward_rate = self._get_forward_rate_for_date(
                base_currency, quote_currency, today, maturity_date, days_ahead
            )
            
            return forward_rate.rate if forward_rate else None
            
        except Exception as e:
            logger.error(f"Error estimating forward rate: {e}")
            return None
