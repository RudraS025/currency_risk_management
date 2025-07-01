"""
Real Forward P&L Calculator for 2025 Currency Risk Management.
Uses actual forward rates data to calculate realistic P&L scenarios.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
import logging

from ..data_providers.real_forward_rates_2025 import RealForwardRatesProvider2025, RealForwardRate
from ..models.letter_of_credit import LetterOfCredit

logger = logging.getLogger(__name__)


@dataclass
class RealPLResult:
    """Real P&L calculation result"""
    date: str
    forward_rate: float
    pl_amount: float
    pl_percentage: float
    cumulative_pl: float
    days_to_maturity: int
    rate_change: float
    source: str = "Real_2025_Data"


@dataclass
class RealScenarioResult:
    """Real scenario analysis result"""
    scenario_name: str
    rate_shift: float
    final_pl: float
    max_profit: float
    max_loss: float
    profit_probability: float
    var_95: float  # Value at Risk at 95% confidence
    expected_pl: float


class RealForwardPLCalculator2025:
    """
    Real Forward P&L Calculator using actual 2025 market data.
    Provides realistic P&L calculations for currency risk management.
    """
    
    def __init__(self):
        """Initialize with real forward rates provider."""
        self.forward_provider = RealForwardRatesProvider2025()
        logger.info("Initialized RealForwardPLCalculator2025 with actual market data")
    
    def calculate_daily_pl(self, lc: LetterOfCredit, start_date: Optional[str] = None) -> List[RealPLResult]:
        """
        Calculate daily P&L using real forward rates.
        
        Args:
            lc: Letter of Credit object
            start_date: Start date for calculations (defaults to LC issue date)
            
        Returns:
            List of daily P&L results
        """
        if start_date is None:
            start_date = lc.issue_date
        
        # Convert dates to strings if they're datetime objects
        start_date_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)
        maturity_date_str = lc.maturity_date.strftime("%Y-%m-%d") if hasattr(lc.maturity_date, 'strftime') else str(lc.maturity_date)
        
        logger.info(f"Calculating real daily P&L for LC from {start_date_str} to {maturity_date_str}")
        logger.info(f"LC Amount: ${lc.total_value:,.2f}")
        logger.info(f"Contract Rate: {lc.contract_rate:.4f}")
        
        # Get daily forward rates
        daily_rates = self.forward_provider.get_daily_forward_rates(
            base_currency='USD',
            quote_currency='INR',
            maturity_date=maturity_date_str,
            start_date=start_date_str,
            end_date=maturity_date_str
        )
        
        if not daily_rates:
            logger.error("No real forward rates available for the specified period")
            return []
        
        pl_results = []
        cumulative_pl = 0.0
        previous_rate = lc.contract_rate
        
        # Sort dates for proper chronological order
        sorted_dates = sorted(daily_rates.keys())
        
        for date_str in sorted_dates:
            forward_rate_obj = daily_rates[date_str]
            forward_rate = forward_rate_obj.rate
            
            # Calculate P&L
            # For a USD/INR LC where we receive USD and pay INR:
            # If forward rate > contract rate, we gain (can buy INR cheaper in forward market)
            # If forward rate < contract rate, we lose (must buy INR more expensive in forward market)
            
            rate_difference = forward_rate - lc.contract_rate
            pl_amount = lc.total_value * rate_difference
            pl_percentage = (rate_difference / lc.contract_rate) * 100
            
            cumulative_pl += (forward_rate - previous_rate) * lc.total_value
            rate_change = forward_rate - previous_rate
            
            result = RealPLResult(
                date=date_str,
                forward_rate=forward_rate,
                pl_amount=pl_amount,
                pl_percentage=pl_percentage,
                cumulative_pl=cumulative_pl,
                days_to_maturity=forward_rate_obj.days_to_maturity,
                rate_change=rate_change,
                source="Real_2025_Data"
            )
            
            pl_results.append(result)
            previous_rate = forward_rate
        
        logger.info(f"Calculated {len(pl_results)} daily P&L points")
        
        if pl_results:
            final_pl = pl_results[-1].pl_amount
            max_profit = max(r.pl_amount for r in pl_results)
            max_loss = min(r.pl_amount for r in pl_results)
            
            logger.info(f"P&L Summary:")
            logger.info(f"  Final P&L: ${final_pl:,.2f}")
            logger.info(f"  Max Profit: ${max_profit:,.2f}")
            logger.info(f"  Max Loss: ${max_loss:,.2f}")
        
        return pl_results
    
    def calculate_scenario_analysis(self, lc: LetterOfCredit, 
                                   start_date: Optional[str] = None) -> List[RealScenarioResult]:
        """
        Calculate scenario analysis based on real forward rate volatility.
        
        Args:
            lc: Letter of Credit object
            start_date: Start date for analysis
            
        Returns:
            List of scenario results
        """
        logger.info("Calculating scenario analysis based on real forward rate data")
        
        # Get base P&L calculation
        base_pl = self.calculate_daily_pl(lc, start_date)
        if not base_pl:
            return []
        
        # Calculate historical volatility from real data
        rates = [r.forward_rate for r in base_pl]
        rate_changes = np.diff(rates) / rates[:-1]
        daily_volatility = np.std(rate_changes)
        
        logger.info(f"Calculated daily volatility: {daily_volatility:.4f}")
        
        scenarios = []
        
        # Define realistic scenarios based on market conditions
        scenario_configs = [
            ("Base Case", 0.0),
            ("INR Weakens 2%", 0.02),
            ("INR Weakens 5%", 0.05),
            ("INR Strengthens 2%", -0.02),
            ("INR Strengthens 5%", -0.05),
            ("High Volatility (+1 Std)", daily_volatility),
            ("High Volatility (-1 Std)", -daily_volatility),
            ("Extreme Bull (+2 Std)", 2 * daily_volatility),
            ("Extreme Bear (-2 Std)", -2 * daily_volatility),
        ]
        
        for scenario_name, rate_shift in scenario_configs:
            scenario_results = []
            
            for pl_result in base_pl:
                # Apply rate shift
                shifted_rate = pl_result.forward_rate * (1 + rate_shift)
                
                # Recalculate P&L with shifted rate
                rate_difference = shifted_rate - lc.contract_rate
                pl_amount = lc.total_value * rate_difference
                
                scenario_results.append(pl_amount)
            
            if scenario_results:
                final_pl = scenario_results[-1]
                max_profit = max(scenario_results)
                max_loss = min(scenario_results)
                expected_pl = np.mean(scenario_results)
                var_95 = np.percentile(scenario_results, 5)  # 5th percentile as VaR
                
                # Simple probability calculation (profit if final PL > 0)
                profit_probability = 1.0 if final_pl > 0 else 0.0
                
                scenario = RealScenarioResult(
                    scenario_name=scenario_name,
                    rate_shift=rate_shift,
                    final_pl=final_pl,
                    max_profit=max_profit,
                    max_loss=max_loss,
                    profit_probability=profit_probability,
                    var_95=var_95,
                    expected_pl=expected_pl
                )
                
                scenarios.append(scenario)
                
                logger.info(f"Scenario '{scenario_name}': Final P&L ${final_pl:,.2f}")
        
        return scenarios
    
    def find_optimal_dates(self, lc: LetterOfCredit, 
                          start_date: Optional[str] = None) -> Dict[str, Tuple[str, float]]:
        """
        Find optimal dates for P&L based on real forward rates.
        
        Args:
            lc: Letter of Credit object
            start_date: Start date for analysis
            
        Returns:
            Dictionary with optimal dates and values
        """
        pl_results = self.calculate_daily_pl(lc, start_date)
        if not pl_results:
            return {}
        
        # Find key dates
        max_profit_result = max(pl_results, key=lambda x: x.pl_amount)
        max_loss_result = min(pl_results, key=lambda x: x.pl_amount)
        
        # Find zero crossing (break-even) points
        zero_crossings = []
        for i in range(1, len(pl_results)):
            if (pl_results[i-1].pl_amount <= 0 <= pl_results[i].pl_amount or 
                pl_results[i-1].pl_amount >= 0 >= pl_results[i].pl_amount):
                zero_crossings.append(pl_results[i])
        
        optimal_dates = {
            'max_profit': (max_profit_result.date, max_profit_result.pl_amount),
            'max_loss': (max_loss_result.date, max_loss_result.pl_amount),
            'final': (pl_results[-1].date, pl_results[-1].pl_amount),
        }
        
        if zero_crossings:
            optimal_dates['break_even'] = (zero_crossings[0].date, zero_crossings[0].pl_amount)
        
        logger.info("Optimal dates identified:")
        for key, (date, amount) in optimal_dates.items():
            logger.info(f"  {key}: {date} (${amount:,.2f})")
        
        return optimal_dates
    
    def get_risk_metrics(self, lc: LetterOfCredit, 
                        start_date: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate risk metrics based on real forward rate data.
        
        Args:
            lc: Letter of Credit object
            start_date: Start date for analysis
            
        Returns:
            Dictionary of risk metrics
        """
        pl_results = self.calculate_daily_pl(lc, start_date)
        if not pl_results:
            return {}
        
        pl_amounts = [r.pl_amount for r in pl_results]
        rates = [r.forward_rate for r in pl_results]
        
        # Calculate metrics
        max_profit = max(pl_amounts)
        max_loss = min(pl_amounts)
        final_pl = pl_amounts[-1]
        avg_pl = np.mean(pl_amounts)
        
        # Volatility metrics
        pl_volatility = np.std(pl_amounts)
        rate_volatility = np.std(rates)
        
        # Risk ratios
        profit_loss_ratio = abs(max_profit / max_loss) if max_loss != 0 else float('inf')
        
        # Value at Risk (VaR)
        var_95 = np.percentile(pl_amounts, 5)
        var_99 = np.percentile(pl_amounts, 1)
        
        metrics = {
            'max_profit': max_profit,
            'max_loss': max_loss,
            'final_pl': final_pl,
            'average_pl': avg_pl,
            'pl_volatility': pl_volatility,
            'rate_volatility': rate_volatility,
            'profit_loss_ratio': profit_loss_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'total_exposure': lc.total_value,
            'rate_range': max(rates) - min(rates),
            'days_to_maturity': pl_results[0].days_to_maturity if pl_results else 0
        }
        
        logger.info("Risk metrics calculated:")
        for key, value in metrics.items():
            if 'amount' in key or 'pl' in key or 'var' in key or 'exposure' in key:
                logger.info(f"  {key}: ${value:,.2f}")
            elif 'ratio' in key:
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value:.4f}")
        
        return metrics
    
    def is_real_data_available(self, start_date: str, end_date: str) -> bool:
        """Check if real data is available for the given date range."""
        return self.forward_provider.is_data_available(start_date, end_date)
    
    def get_data_summary(self) -> Dict[str, any]:
        """Get summary of available real data."""
        coverage = self.forward_provider.get_data_coverage()
        
        return {
            "provider": "RealForwardRatesProvider2025",
            "data_type": "Actual_Market_Forward_Rates",
            "coverage": coverage,
            "currency_pair": "USD/INR",
            "spot_rate": self.forward_provider.get_spot_rate(),
            "reliability": "High - User Provided Market Data"
        }
