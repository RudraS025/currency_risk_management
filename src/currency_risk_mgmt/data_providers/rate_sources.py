"""
Rate sources for fetching forex data from various APIs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import requests
import yfinance as yf
import logging
import time

logger = logging.getLogger(__name__)


class RateSource(ABC):
    """Abstract base class for forex rate sources."""
    
    def __init__(self, name: str):
        self.name = name
        self.last_request_time = 0
        self.rate_limit_delay = 1  # seconds between requests
    
    @abstractmethod
    def get_current_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get current exchange rate."""
        pass
    
    @abstractmethod
    def get_historical_rates(self, from_currency: str, to_currency: str, 
                           start_date: str, end_date: str) -> Dict[str, float]:
        """Get historical exchange rates."""
        pass
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class YFinanceSource(RateSource):
    """Yahoo Finance data source for forex rates."""
    
    def __init__(self):
        super().__init__("Yahoo Finance")
        self.rate_limit_delay = 0.5  # Yahoo Finance is more lenient
    
    def get_current_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get current USD/INR rate from Yahoo Finance."""
        try:
            self._rate_limit()
            
            # Yahoo Finance uses currency pair format like USDINR=X
            symbol = f"{from_currency}{to_currency}=X"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            current_rate = data['Close'].iloc[-1]
            logger.info(f"Retrieved {from_currency}/{to_currency} rate: {current_rate}")
            
            return float(current_rate)
            
        except Exception as e:
            logger.error(f"Error fetching rate from Yahoo Finance: {e}")
            return None
    
    def get_historical_rates(self, from_currency: str, to_currency: str, 
                           start_date: str, end_date: str) -> Dict[str, float]:
        """Get historical rates from Yahoo Finance."""
        try:
            self._rate_limit()
            
            symbol = f"{from_currency}{to_currency}=X"
            ticker = yf.Ticker(symbol)
            
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No historical data available for {symbol}")
                return {}
            
            # Convert to dictionary with date strings as keys
            rates = {}
            for date, row in data.iterrows():
                date_str = date.strftime("%Y-%m-%d")
                rates[date_str] = float(row['Close'])
            
            logger.info(f"Retrieved {len(rates)} historical rates for {from_currency}/{to_currency}")
            return rates
            
        except Exception as e:
            logger.error(f"Error fetching historical rates from Yahoo Finance: {e}")
            return {}


class ExchangeRateAPISource(RateSource):
    """ExchangeRate-API source for forex rates."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ExchangeRate-API")
        self.api_key = api_key
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.rate_limit_delay = 1.0  # Free tier has limits
    
    def get_current_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get current exchange rate from ExchangeRate-API."""
        try:
            self._rate_limit()
            
            if self.api_key:
                url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
            else:
                # Use free tier without API key (limited requests)
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if self.api_key:
                # Paid API response format
                if data.get('result') == 'success':
                    rate = data.get('conversion_rate')
                    logger.info(f"Retrieved {from_currency}/{to_currency} rate: {rate}")
                    return float(rate)
            else:
                # Free API response format
                rates = data.get('rates', {})
                if to_currency in rates:
                    rate = rates[to_currency]
                    logger.info(f"Retrieved {from_currency}/{to_currency} rate: {rate}")
                    return float(rate)
            
            logger.warning(f"Rate not found for {from_currency}/{to_currency}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error fetching rate from ExchangeRate-API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching rate from ExchangeRate-API: {e}")
            return None
    
    def get_historical_rates(self, from_currency: str, to_currency: str, 
                           start_date: str, end_date: str) -> Dict[str, float]:
        """Get historical rates from ExchangeRate-API."""
        try:
            if not self.api_key:
                logger.warning("Historical data requires API key for ExchangeRate-API")
                return {}
            
            rates = {}
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            current_date = start
            while current_date <= end:
                self._rate_limit()
                
                date_str = current_date.strftime("%Y-%m-%d")
                url = f"{self.base_url}/{self.api_key}/history/{from_currency}/{date_str}"
                
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('result') == 'success':
                        conversion_rates = data.get('conversion_rates', {})
                        if to_currency in conversion_rates:
                            rates[date_str] = float(conversion_rates[to_currency])
                
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Failed to fetch rate for {date_str}: {e}")
                
                current_date += timedelta(days=1)
            
            logger.info(f"Retrieved {len(rates)} historical rates for {from_currency}/{to_currency}")
            return rates
            
        except Exception as e:
            logger.error(f"Error fetching historical rates from ExchangeRate-API: {e}")
            return {}


class FreeCurrencyAPISource(RateSource):
    """Free Currency API source (backup option)."""
    
    def __init__(self):
        super().__init__("FreeCurrencyAPI")
        self.base_url = "https://api.freecurrencyapi.com/v1"
        self.rate_limit_delay = 2.0
    
    def get_current_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get current exchange rate from FreeCurrencyAPI."""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/latest"
            params = {
                'base_currency': from_currency,
                'currencies': to_currency
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('data', {})
            
            if to_currency in rates:
                rate = rates[to_currency]
                logger.info(f"Retrieved {from_currency}/{to_currency} rate: {rate}")
                return float(rate)
            
            logger.warning(f"Rate not found for {from_currency}/{to_currency}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching rate from FreeCurrencyAPI: {e}")
            return None
    
    def get_historical_rates(self, from_currency: str, to_currency: str, 
                           start_date: str, end_date: str) -> Dict[str, float]:
        """Historical rates not available in free tier."""
        logger.warning("Historical rates not available in FreeCurrencyAPI free tier")
        return {}
