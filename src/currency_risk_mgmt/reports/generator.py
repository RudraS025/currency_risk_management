"""
Report generator for currency risk management system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from pathlib import Path
import pandas as pd
from ..models.letter_of_credit import LetterOfCredit
from ..calculators.profit_loss import ProfitLossCalculator
from ..calculators.risk_metrics import RiskMetricsCalculator
from ..data_providers.forex_provider import ForexDataProvider

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive reports for currency risk management.
    """
    
    def __init__(self, forex_provider: Optional[ForexDataProvider] = None):
        """
        Initialize the report generator.
        
        Args:
            forex_provider: Forex data provider instance
        """
        self.forex_provider = forex_provider or ForexDataProvider()
        self.pl_calculator = ProfitLossCalculator(self.forex_provider)
        self.risk_calculator = RiskMetricsCalculator(self.forex_provider)
    
    def generate_lc_summary_report(self, lc: LetterOfCredit, 
                                 base_currency: str = "INR") -> Dict[str, Any]:
        """
        Generate a comprehensive summary report for a single LC.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for financial calculations
        
        Returns:
            Dictionary containing complete LC analysis
        """
        try:
            logger.info(f"Generating summary report for LC {lc.lc_id}")
            
            # Basic LC information
            lc_info = lc.to_dict()
            
            # Current P&L analysis
            current_pl = self.pl_calculator.calculate_current_pl(lc, base_currency)
            
            # Forward P&L projection
            forward_pl = self.pl_calculator.calculate_forward_pl_projection(lc, base_currency)
            
            # Risk metrics
            var_analysis = self.risk_calculator.calculate_value_at_risk(lc, base_currency=base_currency)
            expected_shortfall = self.risk_calculator.calculate_expected_shortfall(lc, base_currency=base_currency)
            
            # Scenario analysis (±10%, ±20%, ±30% rate changes)
            current_rate = current_pl.get('current_rate', 0)
            if current_rate > 0:
                scenarios = [
                    current_rate * 0.7,   # -30%
                    current_rate * 0.8,   # -20%
                    current_rate * 0.9,   # -10%
                    current_rate,         # Current
                    current_rate * 1.1,   # +10%
                    current_rate * 1.2,   # +20%
                    current_rate * 1.3    # +30%
                ]
                scenario_analysis = self.pl_calculator.calculate_scenario_analysis(lc, scenarios, base_currency)
            else:
                scenario_analysis = []
            
            # Risk-adjusted metrics
            risk_adjusted = self.risk_calculator.calculate_risk_adjusted_return(lc, base_currency)
            
            # Compile comprehensive report
            report = {
                'report_type': 'LC_SUMMARY',
                'report_id': f"LC_RPT_{lc.lc_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generation_timestamp': datetime.now().isoformat(),
                'lc_information': lc_info,
                'current_profit_loss': current_pl,
                'forward_projection': forward_pl,
                'risk_metrics': {
                    'value_at_risk': var_analysis,
                    'expected_shortfall': expected_shortfall,
                    'risk_adjusted_return': risk_adjusted
                },
                'scenario_analysis': scenario_analysis,
                'recommendations': self._generate_recommendations(lc, current_pl, var_analysis),
                'data_sources': self._get_data_source_info(),
                'base_currency': base_currency
            }
            
            logger.info(f"Successfully generated summary report for LC {lc.lc_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating summary report for LC {lc.lc_id}: {e}")
            return self._empty_report("LC_SUMMARY")
    
    def generate_portfolio_report(self, lcs: List[LetterOfCredit], 
                                base_currency: str = "INR") -> Dict[str, Any]:
        """
        Generate a comprehensive portfolio report for multiple LCs.
        
        Args:
            lcs: List of Letter of Credit instances
            base_currency: Currency for financial calculations
        
        Returns:
            Dictionary containing portfolio analysis
        """
        try:
            logger.info(f"Generating portfolio report for {len(lcs)} LCs")
            
            # Portfolio-level P&L
            portfolio_pl = self.pl_calculator.calculate_portfolio_pl(lcs, base_currency)
            
            # Portfolio risk metrics
            portfolio_risk = self.risk_calculator.calculate_portfolio_risk(lcs, base_currency)
            
            # Individual LC summaries
            lc_summaries = []
            for lc in lcs:
                pl = self.pl_calculator.calculate_current_pl(lc, base_currency)
                var = self.risk_calculator.calculate_value_at_risk(lc, base_currency=base_currency)
                
                summary = {
                    'lc_id': lc.lc_id,
                    'commodity': lc.commodity,
                    'total_value_foreign': lc.total_value,
                    'currency': lc.currency,
                    'days_remaining': lc.days_remaining,
                    'unrealized_pl': pl.get('unrealized_pl', 0),
                    'pl_percentage': pl.get('pl_percentage', 0),
                    'var_absolute': var.get('var_absolute', 0),
                    'risk_level': self._assess_risk_level(var.get('var_percentage', 0))
                }
                lc_summaries.append(summary)
            
            # Currency exposure analysis
            currency_breakdown = self._analyze_currency_exposure(lcs, base_currency)
            
            # Maturity analysis
            maturity_analysis = self._analyze_maturity_profile(lcs)
            
            # Top performers and risks
            top_performers = sorted(lc_summaries, key=lambda x: x['pl_percentage'], reverse=True)[:5]
            top_risks = sorted(lc_summaries, key=lambda x: x['var_absolute'], reverse=True)[:5]
            
            report = {
                'report_type': 'PORTFOLIO_SUMMARY',
                'report_id': f"PORT_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generation_timestamp': datetime.now().isoformat(),
                'portfolio_summary': {
                    'total_lcs': len(lcs),
                    'total_exposure': portfolio_pl.get('total_value_current', 0),
                    'total_unrealized_pl': portfolio_pl.get('total_unrealized_pl', 0),
                    'portfolio_pl_percentage': portfolio_pl.get('portfolio_pl_percentage', 0),
                    'portfolio_var': portfolio_risk.get('portfolio_var', 0),
                    'diversification_ratio': portfolio_risk.get('diversification_ratio', 0)
                },
                'currency_exposure': currency_breakdown,
                'maturity_profile': maturity_analysis,
                'lc_details': lc_summaries,
                'top_performers': top_performers,
                'top_risks': top_risks,
                'portfolio_recommendations': self._generate_portfolio_recommendations(portfolio_pl, portfolio_risk),
                'base_currency': base_currency
            }
            
            logger.info(f"Successfully generated portfolio report for {len(lcs)} LCs")
            return report
            
        except Exception as e:
            logger.error(f"Error generating portfolio report: {e}")
            return self._empty_report("PORTFOLIO_SUMMARY")
    
    def generate_daily_pnl_report(self, lcs: List[LetterOfCredit], 
                                base_currency: str = "INR") -> Dict[str, Any]:
        """
        Generate daily P&L monitoring report.
        
        Args:
            lcs: List of Letter of Credit instances
            base_currency: Currency for calculations
        
        Returns:
            Dictionary containing daily P&L analysis
        """
        try:
            logger.info(f"Generating daily P&L report for {len(lcs)} LCs")
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Calculate current P&L for all LCs
            daily_pnl_data = []
            total_unrealized_pl = 0
            
            for lc in lcs:
                pl = self.pl_calculator.calculate_current_pl(lc, base_currency)
                
                if pl.get('unrealized_pl') is not None:
                    total_unrealized_pl += pl['unrealized_pl']
                    
                    daily_pnl_data.append({
                        'lc_id': lc.lc_id,
                        'commodity': lc.commodity,
                        'current_rate': pl.get('current_rate', 0),
                        'signing_rate': pl.get('signing_rate', 0),
                        'rate_change_pct': ((pl.get('current_rate', 0) - pl.get('signing_rate', 0)) / 
                                          pl.get('signing_rate', 1)) * 100,
                        'unrealized_pl': pl.get('unrealized_pl', 0),
                        'pl_percentage': pl.get('pl_percentage', 0),
                        'daily_pl': pl.get('daily_pl', 0),
                        'days_remaining': lc.days_remaining
                    })
            
            # Sort by P&L impact
            daily_pnl_data.sort(key=lambda x: x['unrealized_pl'], reverse=True)
            
            # Market summary
            market_summary = self._generate_market_summary()
            
            report = {
                'report_type': 'DAILY_PNL',
                'report_id': f"DAILY_RPT_{datetime.now().strftime('%Y%m%d')}",
                'generation_timestamp': datetime.now().isoformat(),
                'report_date': today,
                'summary': {
                    'total_lcs': len(lcs),
                    'total_unrealized_pl': total_unrealized_pl,
                    'positive_pl_count': len([x for x in daily_pnl_data if x['unrealized_pl'] > 0]),
                    'negative_pl_count': len([x for x in daily_pnl_data if x['unrealized_pl'] < 0])
                },
                'lc_performance': daily_pnl_data,
                'market_summary': market_summary,
                'alerts': self._generate_alerts(daily_pnl_data),
                'base_currency': base_currency
            }
            
            logger.info(f"Generated daily P&L report: Total P&L {base_currency} {total_unrealized_pl:,.2f}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily P&L report: {e}")
            return self._empty_report("DAILY_PNL")
    
    def export_report_to_excel(self, report: Dict[str, Any], 
                             filename: Optional[str] = None) -> str:
        """
        Export report to Excel format.
        
        Args:
            report: Report dictionary
            filename: Optional filename for the Excel file
        
        Returns:
            Path to the created Excel file
        """
        try:
            if filename is None:
                filename = f"{report.get('report_type', 'REPORT')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            filepath = Path(filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Summary sheet
                if report.get('report_type') == 'LC_SUMMARY':
                    self._write_lc_summary_to_excel(report, writer)
                    
                elif report.get('report_type') == 'PORTFOLIO_SUMMARY':
                    self._write_portfolio_summary_to_excel(report, writer)
                    
                elif report.get('report_type') == 'DAILY_PNL':
                    self._write_daily_pnl_to_excel(report, writer)
            
            logger.info(f"Report exported to Excel: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting report to Excel: {e}")
            return ""
    
    def save_report_json(self, report: Dict[str, Any], 
                        filename: Optional[str] = None) -> str:
        """
        Save report as JSON file.
        
        Args:
            report: Report dictionary
            filename: Optional filename for the JSON file
        
        Returns:
            Path to the created JSON file
        """
        try:
            if filename is None:
                filename = f"{report.get('report_type', 'REPORT')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Report saved as JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving report as JSON: {e}")
            return ""
    
    def _generate_recommendations(self, lc: LetterOfCredit, 
                                pl_result: Dict[str, Any],
                                var_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # P&L based recommendations
        pl_pct = pl_result.get('pl_percentage', 0)
        if pl_pct > 10:
            recommendations.append("Consider partial hedging to lock in profits")
        elif pl_pct < -10:
            recommendations.append("Monitor closely - significant unrealized loss")
        
        # Risk based recommendations
        var_pct = var_result.get('var_percentage', 0)
        if var_pct > 15:
            recommendations.append("High volatility detected - consider hedging strategies")
        
        # Time based recommendations
        if lc.days_remaining < 30:
            recommendations.append("LC approaching maturity - prepare for settlement")
        elif lc.days_remaining > 60:
            recommendations.append("Long-term exposure - monitor regularly")
        
        return recommendations
    
    def _generate_portfolio_recommendations(self, portfolio_pl: Dict[str, Any],
                                          portfolio_risk: Dict[str, Any]) -> List[str]:
        """Generate portfolio-level recommendations."""
        recommendations = []
        
        # Diversification recommendations
        div_ratio = portfolio_risk.get('diversification_ratio', 0)
        if div_ratio < 0.2:
            recommendations.append("Consider diversifying across more currencies")
        
        # Concentration risk
        conc_ratio = portfolio_risk.get('concentration_ratio', 0)
        if conc_ratio > 0.5:
            recommendations.append("High concentration in single currency - consider rebalancing")
        
        # Overall P&L
        total_pl_pct = portfolio_pl.get('portfolio_pl_percentage', 0)
        if total_pl_pct < -5:
            recommendations.append("Portfolio showing significant losses - review hedging strategy")
        
        return recommendations
    
    def _analyze_currency_exposure(self, lcs: List[LetterOfCredit], 
                                 base_currency: str) -> Dict[str, Any]:
        """Analyze currency exposure breakdown."""
        currency_exposure = {}
        total_exposure = 0
        
        for lc in lcs:
            current_rate = self.forex_provider.get_current_rate(lc.currency, base_currency)
            if current_rate:
                exposure = lc.total_value * current_rate
                total_exposure += exposure
                
                if lc.currency not in currency_exposure:
                    currency_exposure[lc.currency] = {
                        'exposure': 0,
                        'lc_count': 0,
                        'commodities': set()
                    }
                
                currency_exposure[lc.currency]['exposure'] += exposure
                currency_exposure[lc.currency]['lc_count'] += 1
                currency_exposure[lc.currency]['commodities'].add(lc.commodity)
        
        # Convert sets to lists for JSON serialization
        for currency in currency_exposure:
            currency_exposure[currency]['commodities'] = list(currency_exposure[currency]['commodities'])
            currency_exposure[currency]['percentage'] = (currency_exposure[currency]['exposure'] / total_exposure * 100) if total_exposure > 0 else 0
        
        return currency_exposure
    
    def _analyze_maturity_profile(self, lcs: List[LetterOfCredit]) -> Dict[str, Any]:
        """Analyze maturity profile of LCs."""
        maturity_buckets = {
            '0-30 days': 0,
            '31-60 days': 0,
            '61-90 days': 0,
            '90+ days': 0,
            'matured': 0
        }
        
        for lc in lcs:
            days_remaining = lc.days_remaining
            
            if lc.is_matured:
                maturity_buckets['matured'] += 1
            elif days_remaining <= 30:
                maturity_buckets['0-30 days'] += 1
            elif days_remaining <= 60:
                maturity_buckets['31-60 days'] += 1
            elif days_remaining <= 90:
                maturity_buckets['61-90 days'] += 1
            else:
                maturity_buckets['90+ days'] += 1
        
        return maturity_buckets
    
    def _generate_market_summary(self) -> Dict[str, Any]:
        """Generate market summary information."""
        try:
            # Get current major rates
            usd_inr = self.forex_provider.get_current_rate('USD', 'INR')
            eur_inr = self.forex_provider.get_current_rate('EUR', 'INR')
            
            return {
                'usd_inr_rate': usd_inr,
                'eur_inr_rate': eur_inr,
                'data_timestamp': datetime.now().isoformat(),
                'market_status': 'Active' if datetime.now().weekday() < 5 else 'Closed'
            }
        except Exception:
            return {}
    
    def _generate_alerts(self, pnl_data: List[Dict[str, Any]]) -> List[str]:
        """Generate alerts based on P&L data."""
        alerts = []
        
        for lc_data in pnl_data:
            if lc_data['pl_percentage'] < -15:
                alerts.append(f"HIGH LOSS ALERT: {lc_data['lc_id']} showing {lc_data['pl_percentage']:.1f}% loss")
            
            if lc_data['days_remaining'] <= 7:
                alerts.append(f"MATURITY ALERT: {lc_data['lc_id']} maturing in {lc_data['days_remaining']} days")
            
            if abs(lc_data['rate_change_pct']) > 10:
                alerts.append(f"VOLATILITY ALERT: {lc_data['lc_id']} rate changed by {lc_data['rate_change_pct']:.1f}%")
        
        return alerts
    
    def _assess_risk_level(self, var_percentage: float) -> str:
        """Assess risk level based on VaR percentage."""
        if var_percentage < 5:
            return "Low"
        elif var_percentage < 15:
            return "Medium"
        else:
            return "High"
    
    def _get_data_source_info(self) -> Dict[str, Any]:
        """Get information about data sources."""
        health = self.forex_provider.health_check()
        cache_stats = self.forex_provider.get_cache_stats()
        
        return {
            'source_health': health,
            'cache_statistics': cache_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def _write_lc_summary_to_excel(self, report: Dict[str, Any], writer):
        """Write LC summary report to Excel."""
        # Basic info
        lc_info = pd.DataFrame([report['lc_information']])
        lc_info.to_excel(writer, sheet_name='LC_Info', index=False)
        
        # P&L data
        pl_data = pd.DataFrame([report['current_profit_loss']])
        pl_data.to_excel(writer, sheet_name='Current_PL', index=False)
        
        # Scenario analysis
        if report.get('scenario_analysis'):
            scenario_df = pd.DataFrame(report['scenario_analysis'])
            scenario_df.to_excel(writer, sheet_name='Scenarios', index=False)
    
    def _write_portfolio_summary_to_excel(self, report: Dict[str, Any], writer):
        """Write portfolio summary report to Excel."""
        # Portfolio summary
        summary_df = pd.DataFrame([report['portfolio_summary']])
        summary_df.to_excel(writer, sheet_name='Portfolio_Summary', index=False)
        
        # LC details
        lc_details_df = pd.DataFrame(report['lc_details'])
        lc_details_df.to_excel(writer, sheet_name='LC_Details', index=False)
        
        # Currency exposure
        if report.get('currency_exposure'):
            currency_data = []
            for currency, data in report['currency_exposure'].items():
                currency_data.append({
                    'Currency': currency,
                    'Exposure': data['exposure'],
                    'LC_Count': data['lc_count'],
                    'Percentage': data['percentage']
                })
            currency_df = pd.DataFrame(currency_data)
            currency_df.to_excel(writer, sheet_name='Currency_Exposure', index=False)
    
    def _write_daily_pnl_to_excel(self, report: Dict[str, Any], writer):
        """Write daily P&L report to Excel."""
        # Summary
        summary_df = pd.DataFrame([report['summary']])
        summary_df.to_excel(writer, sheet_name='Daily_Summary', index=False)
        
        # LC performance
        performance_df = pd.DataFrame(report['lc_performance'])
        performance_df.to_excel(writer, sheet_name='LC_Performance', index=False)
    
    def _empty_report(self, report_type: str) -> Dict[str, Any]:
        """Return empty report structure."""
        return {
            'report_type': report_type,
            'report_id': f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generation_timestamp': datetime.now().isoformat(),
            'error': 'Failed to generate report',
            'data': {}
        }
