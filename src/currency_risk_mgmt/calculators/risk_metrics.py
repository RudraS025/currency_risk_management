"""
Risk metrics calculator for currency risk management.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging
from ..models.letter_of_credit import LetterOfCredit
from ..data_providers.forex_provider import ForexDataProvider

logger = logging.getLogger(__name__)


class RiskMetricsCalculator:
    """
    Calculates various risk metrics for currency exposure in international trade.
    """
    
    def __init__(self, forex_provider: Optional[ForexDataProvider] = None):
        """
        Initialize the risk metrics calculator.
        
        Args:
            forex_provider: Forex data provider instance
        """
        self.forex_provider = forex_provider or ForexDataProvider()
    
    def calculate_value_at_risk(self, lc: LetterOfCredit, confidence_level: float = 0.95,
                              time_horizon_days: int = 30, base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR) for a Letter of Credit.
        
        Args:
            lc: Letter of Credit instance
            confidence_level: Confidence level (0.95 for 95% VaR)
            time_horizon_days: Time horizon in days
            base_currency: Currency for VaR calculation
        
        Returns:
            Dictionary containing VaR calculations
        """
        try:
            # Get historical data for volatility calculation
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            historical_rates = self.forex_provider.get_historical_rates(
                lc.currency, base_currency, start_date, end_date
            )
            
            if len(historical_rates) < 20:
                logger.warning(f"Insufficient historical data for VaR calculation: {len(historical_rates)} points")
                return self._empty_var_result()
            
            # Calculate daily returns
            rates_list = [historical_rates[date] for date in sorted(historical_rates.keys())]
            daily_returns = []
            
            for i in range(1, len(rates_list)):
                daily_return = (rates_list[i] - rates_list[i-1]) / rates_list[i-1]
                daily_returns.append(daily_return)
            
            if not daily_returns:
                return self._empty_var_result()
            
            # Calculate volatility (standard deviation of returns)
            mean_return = sum(daily_returns) / len(daily_returns)
            variance = sum((r - mean_return) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
            daily_volatility = math.sqrt(variance)
            
            # Scale volatility to time horizon
            volatility_scaled = daily_volatility * math.sqrt(time_horizon_days)
            
            # Calculate VaR using normal distribution assumption
            from math import sqrt, log
            import statistics
            
            # Z-score for confidence level
            z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
            z_score = z_scores.get(confidence_level, 1.65)
            
            # Current position value in base currency
            current_rate = self.forex_provider.get_current_rate(lc.currency, base_currency)
            if current_rate is None:
                return self._empty_var_result()
            
            position_value = lc.total_value * current_rate
            
            # VaR calculation
            var_absolute = position_value * volatility_scaled * z_score
            var_percentage = volatility_scaled * z_score * 100
            
            result = {
                'lc_id': lc.lc_id,
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon_days,
                'position_value': position_value,
                'daily_volatility': daily_volatility,
                'volatility_scaled': volatility_scaled,
                'var_absolute': var_absolute,
                'var_percentage': var_percentage,
                'current_rate': current_rate,
                'foreign_currency': lc.currency,
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data_points_used': len(daily_returns)
            }
            
            logger.info(f"VaR calculated for {lc.lc_id}: {base_currency} {var_absolute:,.2f} ({var_percentage:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating VaR for {lc.lc_id}: {e}")
            return self._empty_var_result()
    
    def calculate_expected_shortfall(self, lc: LetterOfCredit, confidence_level: float = 0.95,
                                   time_horizon_days: int = 30, base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate Expected Shortfall (Conditional VaR) for a Letter of Credit.
        
        Args:
            lc: Letter of Credit instance
            confidence_level: Confidence level
            time_horizon_days: Time horizon in days
            base_currency: Currency for calculation
        
        Returns:
            Dictionary containing Expected Shortfall calculations
        """
        try:
            # First calculate VaR
            var_result = self.calculate_value_at_risk(lc, confidence_level, time_horizon_days, base_currency)
            
            if not var_result.get('daily_volatility'):
                return self._empty_es_result()
            
            # Get historical returns for empirical ES calculation
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            historical_rates = self.forex_provider.get_historical_rates(
                lc.currency, base_currency, start_date, end_date
            )
            
            rates_list = [historical_rates[date] for date in sorted(historical_rates.keys())]
            daily_returns = []
            
            for i in range(1, len(rates_list)):
                daily_return = (rates_list[i] - rates_list[i-1]) / rates_list[i-1]
                daily_returns.append(daily_return)
            
            # Sort returns (worst first)
            daily_returns.sort()
            
            # Calculate empirical expected shortfall
            cutoff_index = int(len(daily_returns) * (1 - confidence_level))
            worst_returns = daily_returns[:max(cutoff_index, 1)]
            
            expected_shortfall_return = sum(worst_returns) / len(worst_returns)
            
            # Scale to time horizon
            es_scaled = expected_shortfall_return * math.sqrt(time_horizon_days)
            
            position_value = var_result['position_value']
            es_absolute = abs(position_value * es_scaled)
            es_percentage = abs(es_scaled * 100)
            
            result = {
                'lc_id': lc.lc_id,
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon_days,
                'position_value': position_value,
                'expected_shortfall_absolute': es_absolute,
                'expected_shortfall_percentage': es_percentage,
                'var_absolute': var_result['var_absolute'],
                'var_percentage': var_result['var_percentage'],
                'es_to_var_ratio': es_absolute / var_result['var_absolute'] if var_result['var_absolute'] > 0 else 0,
                'foreign_currency': lc.currency,
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'worst_scenarios_count': len(worst_returns)
            }
            
            logger.info(f"Expected Shortfall calculated for {lc.lc_id}: {base_currency} {es_absolute:,.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall for {lc.lc_id}: {e}")
            return self._empty_es_result()
    
    def calculate_portfolio_risk(self, lcs: List[LetterOfCredit], 
                               base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate portfolio-level risk metrics.
        
        Args:
            lcs: List of Letter of Credit instances
            base_currency: Currency for risk calculation
        
        Returns:
            Dictionary containing portfolio risk metrics
        """
        try:
            if not lcs:
                return self._empty_portfolio_risk_result()
            
            total_exposure = 0.0
            currency_exposures = {}
            individual_vars = []
            
            # Calculate individual exposures and VaRs
            for lc in lcs:
                current_rate = self.forex_provider.get_current_rate(lc.currency, base_currency)
                if current_rate is None:
                    continue
                
                exposure = lc.total_value * current_rate
                total_exposure += exposure
                
                # Group by currency
                if lc.currency not in currency_exposures:
                    currency_exposures[lc.currency] = {'exposure': 0.0, 'lc_count': 0}
                currency_exposures[lc.currency]['exposure'] += exposure
                currency_exposures[lc.currency]['lc_count'] += 1
                
                # Calculate individual VaR
                var_result = self.calculate_value_at_risk(lc, base_currency=base_currency)
                if var_result.get('var_absolute'):
                    individual_vars.append(var_result['var_absolute'])
            
            # Calculate portfolio-level metrics
            if not individual_vars:
                return self._empty_portfolio_risk_result()
            
            # Simple portfolio VaR (assuming no correlation - conservative)
            portfolio_var = math.sqrt(sum(var ** 2 for var in individual_vars))
            
            # Diversification benefit
            undiversified_var = sum(individual_vars)
            diversification_benefit = undiversified_var - portfolio_var
            diversification_ratio = diversification_benefit / undiversified_var if undiversified_var > 0 else 0
            
            # Concentration risk
            largest_exposure = max(exp['exposure'] for exp in currency_exposures.values())
            concentration_ratio = largest_exposure / total_exposure if total_exposure > 0 else 0
            
            result = {
                'total_lcs': len(lcs),
                'total_exposure': total_exposure,
                'portfolio_var': portfolio_var,
                'undiversified_var': undiversified_var,
                'diversification_benefit': diversification_benefit,
                'diversification_ratio': diversification_ratio,
                'concentration_ratio': concentration_ratio,
                'currency_exposures': currency_exposures,
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"Portfolio risk calculated: VaR {base_currency} {portfolio_var:,.2f}, "
                       f"Concentration {concentration_ratio:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return self._empty_portfolio_risk_result()
    
    def calculate_currency_correlation(self, currency_pairs: List[Tuple[str, str]], 
                                     days_back: int = 90) -> Dict[str, float]:
        """
        Calculate correlation between currency pairs.
        
        Args:
            currency_pairs: List of tuples representing currency pairs
            days_back: Number of days of historical data to use
        
        Returns:
            Dictionary with correlation coefficients
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            all_returns = {}
            
            # Get returns for each currency pair
            for from_curr, to_curr in currency_pairs:
                pair_key = f"{from_curr}/{to_curr}"
                
                rates = self.forex_provider.get_historical_rates(from_curr, to_curr, start_date, end_date)
                
                if len(rates) < 20:
                    continue
                
                rates_list = [rates[date] for date in sorted(rates.keys())]
                returns = []
                
                for i in range(1, len(rates_list)):
                    daily_return = (rates_list[i] - rates_list[i-1]) / rates_list[i-1]
                    returns.append(daily_return)
                
                if returns:
                    all_returns[pair_key] = returns
            
            # Calculate correlations
            correlations = {}
            pairs = list(all_returns.keys())
            
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    pair1, pair2 = pairs[i], pairs[j]
                    
                    returns1 = all_returns[pair1]
                    returns2 = all_returns[pair2]
                    
                    # Align the returns (take minimum length)
                    min_len = min(len(returns1), len(returns2))
                    returns1 = returns1[:min_len]
                    returns2 = returns2[:min_len]
                    
                    if min_len < 10:
                        continue
                    
                    # Calculate correlation coefficient
                    correlation = self._calculate_correlation(returns1, returns2)
                    correlations[f"{pair1}_vs_{pair2}"] = correlation
            
            logger.info(f"Calculated {len(correlations)} currency pair correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating currency correlations: {e}")
            return {}
    
    def calculate_risk_adjusted_return(self, lc: LetterOfCredit, 
                                     base_currency: str = "INR") -> Dict[str, float]:
        """
        Calculate risk-adjusted return metrics (Sharpe ratio equivalent).
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for calculation
        
        Returns:
            Dictionary containing risk-adjusted metrics
        """
        try:
            # Get current P&L
            from .profit_loss import ProfitLossCalculator
            pl_calc = ProfitLossCalculator(self.forex_provider)
            pl_result = pl_calc.calculate_current_pl(lc, base_currency)
            
            if not pl_result.get('unrealized_pl'):
                return {}
            
            # Get VaR
            var_result = self.calculate_value_at_risk(lc, base_currency=base_currency)
            
            if not var_result.get('var_absolute'):
                return {}
            
            # Calculate risk-adjusted metrics
            return_percentage = pl_result['pl_percentage']
            risk_percentage = var_result['var_percentage']
            
            # Risk-adjusted return (return per unit of risk)
            risk_adjusted_return = return_percentage / risk_percentage if risk_percentage > 0 else 0
            
            # Return to VaR ratio
            return_to_var = abs(pl_result['unrealized_pl']) / var_result['var_absolute'] if var_result['var_absolute'] > 0 else 0
            
            result = {
                'lc_id': lc.lc_id,
                'return_percentage': return_percentage,
                'risk_percentage': risk_percentage,
                'risk_adjusted_return': risk_adjusted_return,
                'return_to_var_ratio': return_to_var,
                'unrealized_pl': pl_result['unrealized_pl'],
                'var_absolute': var_result['var_absolute'],
                'base_currency': base_currency,
                'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating risk-adjusted return for {lc.lc_id}: {e}")
            return {}
    
    def _calculate_correlation(self, returns1: List[float], returns2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(returns1)
        if n != len(returns2) or n < 2:
            return 0.0
        
        mean1 = sum(returns1) / n
        mean2 = sum(returns2) / n
        
        numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(n))
        
        sum_sq1 = sum((returns1[i] - mean1) ** 2 for i in range(n))
        sum_sq2 = sum((returns2[i] - mean2) ** 2 for i in range(n))
        
        denominator = math.sqrt(sum_sq1 * sum_sq2)
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _empty_var_result(self) -> Dict[str, float]:
        """Return empty VaR result structure."""
        return {
            'lc_id': '',
            'confidence_level': 0.0,
            'time_horizon_days': 0,
            'position_value': 0.0,
            'daily_volatility': 0.0,
            'volatility_scaled': 0.0,
            'var_absolute': 0.0,
            'var_percentage': 0.0,
            'current_rate': 0.0,
            'foreign_currency': '',
            'base_currency': '',
            'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_points_used': 0
        }
    
    def _empty_es_result(self) -> Dict[str, float]:
        """Return empty Expected Shortfall result structure."""
        return {
            'lc_id': '',
            'confidence_level': 0.0,
            'time_horizon_days': 0,
            'position_value': 0.0,
            'expected_shortfall_absolute': 0.0,
            'expected_shortfall_percentage': 0.0,
            'var_absolute': 0.0,
            'var_percentage': 0.0,
            'es_to_var_ratio': 0.0,
            'foreign_currency': '',
            'base_currency': '',
            'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'worst_scenarios_count': 0
        }
    
    def _empty_portfolio_risk_result(self) -> Dict[str, float]:
        """Return empty portfolio risk result structure."""
        return {
            'total_lcs': 0,
            'total_exposure': 0.0,
            'portfolio_var': 0.0,
            'undiversified_var': 0.0,
            'diversification_benefit': 0.0,
            'diversification_ratio': 0.0,
            'concentration_ratio': 0.0,
            'currency_exposures': {},
            'base_currency': '',
            'calculation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
