"""
Main forex data provider that manages multiple data sources.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from .rate_sources import RateSource, YFinanceSource, ExchangeRateAPISource, FreeCurrencyAPISource

logger = logging.getLogger(__name__)


class ForexDataProvider:
    """
    Main forex data provider that manages multiple sources for reliability.
    Implements fallback mechanism and caching for better performance.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the forex data provider.
        
        Args:
            api_key: Optional API key for premium data sources
        """
        self.api_key = api_key
        self.sources: List[RateSource] = []
        self.cache: Dict[str, Tuple[float, datetime]] = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize data sources in order of preference."""
        # Primary source: Yahoo Finance (reliable and free)
        self.sources.append(YFinanceSource())
        
        # Secondary source: ExchangeRate-API
        self.sources.append(ExchangeRateAPISource(self.api_key))
        
        # Tertiary source: FreeCurrencyAPI (backup)
        self.sources.append(FreeCurrencyAPISource())
        
        logger.info(f"Initialized {len(self.sources)} forex data sources")
    
    def _get_cache_key(self, from_currency: str, to_currency: str) -> str:
        """Generate cache key for currency pair."""
        return f"{from_currency}_{to_currency}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache:
            return False
        
        _, timestamp = self.cache[cache_key]
        return datetime.now() - timestamp < self.cache_duration
    
    def get_current_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get current exchange rate with fallback mechanism.
        
        Args:
            from_currency: Source currency (e.g., 'USD')
            to_currency: Target currency (e.g., 'INR')
        
        Returns:
            Current exchange rate or None if all sources fail
        """
        cache_key = self._get_cache_key(from_currency, to_currency)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            rate, _ = self.cache[cache_key]
            logger.debug(f"Retrieved cached rate for {from_currency}/{to_currency}: {rate}")
            return rate
        
        # Handle same currency
        if from_currency == to_currency:
            return 1.0
        
        # Try each source in order
        for source in self.sources:
            try:
                rate = source.get_current_rate(from_currency, to_currency)
                if rate is not None and rate > 0:
                    # Cache the result
                    self.cache[cache_key] = (rate, datetime.now())
                    logger.info(f"Successfully retrieved rate from {source.name}: {from_currency}/{to_currency} = {rate}")
                    return rate
                    
            except Exception as e:
                logger.warning(f"Source {source.name} failed: {e}")
                continue
        
        logger.error(f"All sources failed to provide rate for {from_currency}/{to_currency}")
        return None
    
    def get_historical_rates(self, from_currency: str, to_currency: str, 
                           start_date: str, end_date: str) -> Dict[str, float]:
        """
        Get historical exchange rates.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Dictionary with dates as keys and rates as values
        """
        if from_currency == to_currency:
            # Generate daily rates of 1.0 for same currency
            rates = {}
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            current_date = start
            while current_date <= end:
                rates[current_date.strftime("%Y-%m-%d")] = 1.0
                current_date += timedelta(days=1)
            
            return rates
        
        # Try each source for historical data
        for source in self.sources:
            try:
                rates = source.get_historical_rates(from_currency, to_currency, start_date, end_date)
                if rates:
                    logger.info(f"Retrieved {len(rates)} historical rates from {source.name}")
                    return rates
                    
            except Exception as e:
                logger.warning(f"Source {source.name} failed for historical data: {e}")
                continue
        
        logger.error(f"All sources failed to provide historical rates for {from_currency}/{to_currency}")
        return {}
    
    def get_forward_rate_estimate(self, from_currency: str, to_currency: str, 
                                days_forward: int) -> Optional[float]:
        """
        Estimate forward rate based on historical volatility.
        This is a simplified implementation - in production, you'd use proper forward rate models.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            days_forward: Number of days in the future
        
        Returns:
            Estimated forward rate
        """
        # Get current rate
        current_rate = self.get_current_rate(from_currency, to_currency)
        if current_rate is None:
            return None
        
        # Get historical rates for volatility calculation
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        historical_rates = self.get_historical_rates(from_currency, to_currency, start_date, end_date)
        
        if len(historical_rates) < 5:
            logger.warning("Insufficient historical data for forward rate estimation")
            return current_rate  # Return current rate as fallback
        
        # Calculate simple volatility (standard deviation of daily returns)
        rates_list = list(historical_rates.values())
        daily_returns = []
        
        for i in range(1, len(rates_list)):
            daily_return = (rates_list[i] - rates_list[i-1]) / rates_list[i-1]
            daily_returns.append(daily_return)
        
        if not daily_returns:
            return current_rate
        
        # Calculate volatility
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        volatility = variance ** 0.5
        
        # Simple forward rate estimate (assuming no drift for simplicity)
        # In practice, you'd incorporate interest rate differentials
        forward_volatility_adjustment = volatility * (days_forward ** 0.5) / (365 ** 0.5)
        
        # For conservative estimate, add slight premium for longer periods
        time_premium = 1 + (days_forward / 365) * 0.02  # 2% annual premium
        
        forward_rate = current_rate * time_premium
        
        logger.info(f"Estimated forward rate for {days_forward} days: {forward_rate}")
        return forward_rate
    
    def get_rate_with_confidence(self, from_currency: str, to_currency: str) -> Tuple[Optional[float], int]:
        """
        Get current rate with confidence score based on number of successful sources.
        
        Returns:
            Tuple of (rate, confidence_score) where confidence_score is 0-100
        """
        rates = []
        
        for source in self.sources:
            try:
                rate = source.get_current_rate(from_currency, to_currency)
                if rate is not None and rate > 0:
                    rates.append(rate)
            except Exception:
                continue
        
        if not rates:
            return None, 0
        
        # Use average if multiple sources available
        avg_rate = sum(rates) / len(rates)
        
        # Confidence based on number of sources and variance
        confidence = min(len(rates) * 30, 90)  # Max 90% confidence
        
        if len(rates) > 1:
            # Reduce confidence if rates vary significantly
            rate_variance = max(rates) - min(rates)
            relative_variance = rate_variance / avg_rate
            
            if relative_variance > 0.05:  # 5% variance
                confidence -= 20
            elif relative_variance > 0.02:  # 2% variance
                confidence -= 10
        
        confidence = max(confidence, 10)  # Minimum 10% confidence
        
        return avg_rate, confidence
    
    def clear_cache(self):
        """Clear the rate cache."""
        self.cache.clear()
        logger.info("Rate cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        valid_entries = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache) - valid_entries
        }
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all data sources."""
        health = {}
        
        for source in self.sources:
            try:
                # Test with USD/INR pair
                rate = source.get_current_rate('USD', 'INR')
                health[source.name] = rate is not None
            except Exception:
                health[source.name] = False
        
        return health
