"""
Visualization engine for currency risk management reports.
"""

from typing import Dict, List, Optional, Any, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import logging
from ..models.letter_of_credit import LetterOfCredit
from ..data_providers.forex_provider import ForexDataProvider

logger = logging.getLogger(__name__)

# Set matplotlib style
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')


class VisualizationEngine:
    """
    Creates visualizations for currency risk management reports.
    """
    
    def __init__(self, forex_provider: Optional[ForexDataProvider] = None):
        """
        Initialize the visualization engine.
        
        Args:
            forex_provider: Forex data provider instance
        """
        self.forex_provider = forex_provider or ForexDataProvider()
        self.color_palette = {
            'profit': '#2E8B57',      # Sea Green
            'loss': '#DC143C',        # Crimson
            'neutral': '#4682B4',     # Steel Blue
            'warning': '#FF8C00',     # Dark Orange
            'background': '#F5F5F5'   # White Smoke
        }
    
    def create_pnl_trend_chart(self, lc: LetterOfCredit, 
                              base_currency: str = "INR",
                              days_back: int = 30) -> go.Figure:
        """
        Create P&L trend chart for a single LC.
        
        Args:
            lc: Letter of Credit instance
            base_currency: Currency for calculations
            days_back: Number of days to show historical data
        
        Returns:
            Plotly figure object
        """
        try:
            # Get historical rates
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            historical_rates = self.forex_provider.get_historical_rates(
                lc.currency, base_currency, start_date, end_date
            )
            
            if not historical_rates:
                return self._create_empty_chart("No historical data available")
            
            # Get signing rate for baseline
            signing_rate = self._get_rate_for_date(historical_rates, lc.signing_date)
            if signing_rate is None:
                return self._create_empty_chart("Signing date rate not available")
            
            # Calculate P&L for each date
            dates = []
            pnl_values = []
            rates = []
            
            for date_str, rate in sorted(historical_rates.items()):
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Only include dates after signing
                if date_obj >= lc.signing_date_obj:
                    lc_value_base_signing = lc.total_value * signing_rate
                    lc_value_base_current = lc.total_value * rate
                    pnl = lc_value_base_current - lc_value_base_signing
                    
                    dates.append(date_obj)
                    pnl_values.append(pnl)
                    rates.append(rate)
            
            if not dates:
                return self._create_empty_chart("No data after signing date")
            
            # Create the chart
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=[f'P&L Trend for LC {lc.lc_id}', 'Exchange Rate'],
                vertical_spacing=0.12,
                specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
            )
            
            # P&L line
            colors = [self.color_palette['profit'] if pnl >= 0 else self.color_palette['loss'] 
                     for pnl in pnl_values]
            
            fig.add_trace(
                go.Scatter(
                    x=dates, y=pnl_values,
                    mode='lines+markers',
                    name=f'P&L ({base_currency})',
                    line=dict(color=self.color_palette['neutral'], width=2),
                    marker=dict(color=colors, size=6),
                    hovertemplate='<b>%{x}</b><br>P&L: %{y:,.0f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
            
            # Exchange rate
            fig.add_trace(
                go.Scatter(
                    x=dates, y=rates,
                    mode='lines',
                    name=f'{lc.currency}/{base_currency}',
                    line=dict(color=self.color_palette['warning'], width=2),
                    hovertemplate='<b>%{x}</b><br>Rate: %{y:.4f}<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add signing rate baseline
            fig.add_hline(y=signing_rate, line_dash="dash", line_color="red", 
                         annotation_text="Signing Rate", row=2, col=1)
            
            # Update layout
            fig.update_layout(
                title=f'Currency Risk Analysis: {lc.commodity} ({lc.quantity} {lc.unit})',
                height=600,
                showlegend=True,
                template='plotly_white',
                margin=dict(t=80, b=40, l=60, r=40)
            )
            
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text=f"P&L ({base_currency})", row=1, col=1)
            fig.update_yaxes(title_text="Exchange Rate", row=2, col=1)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating P&L trend chart: {e}")
            return self._create_empty_chart("Error creating chart")
    
    def create_portfolio_dashboard(self, report_data: Dict[str, Any]) -> go.Figure:
        """
        Create a comprehensive portfolio dashboard.
        
        Args:
            report_data: Portfolio report data
        
        Returns:
            Plotly figure object with multiple subplots
        """
        try:
            # Extract data
            lc_details = report_data.get('lc_details', [])
            currency_exposure = report_data.get('currency_exposure', {})
            maturity_profile = report_data.get('maturity_profile', {})
            
            if not lc_details:
                return self._create_empty_chart("No portfolio data available")
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'P&L Distribution by LC',
                    'Currency Exposure',
                    'Maturity Profile',
                    'Risk vs Return'
                ],
                specs=[
                    [{"type": "bar"}, {"type": "pie"}],
                    [{"type": "bar"}, {"type": "scatter"}]
                ],
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            # 1. P&L Distribution
            lc_ids = [lc['lc_id'] for lc in lc_details]
            pnl_values = [lc['unrealized_pl'] for lc in lc_details]
            pnl_colors = [self.color_palette['profit'] if pnl >= 0 else self.color_palette['loss'] 
                         for pnl in pnl_values]
            
            fig.add_trace(
                go.Bar(
                    x=lc_ids, y=pnl_values,
                    name='P&L by LC',
                    marker_color=pnl_colors,
                    hovertemplate='<b>%{x}</b><br>P&L: %{y:,.0f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # 2. Currency Exposure Pie Chart
            if currency_exposure:
                currencies = list(currency_exposure.keys())
                exposures = [currency_exposure[curr]['exposure'] for curr in currencies]
                
                fig.add_trace(
                    go.Pie(
                        labels=currencies,
                        values=exposures,
                        name="Currency Exposure",
                        hovertemplate='<b>%{label}</b><br>Exposure: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. Maturity Profile
            if maturity_profile:
                maturity_buckets = list(maturity_profile.keys())
                maturity_counts = list(maturity_profile.values())
                
                fig.add_trace(
                    go.Bar(
                        x=maturity_buckets, y=maturity_counts,
                        name='Maturity Profile',
                        marker_color=self.color_palette['neutral'],
                        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # 4. Risk vs Return Scatter
            pl_percentages = [lc['pl_percentage'] for lc in lc_details]
            var_values = [lc['var_absolute'] for lc in lc_details]
            
            fig.add_trace(
                go.Scatter(
                    x=var_values, y=pl_percentages,
                    mode='markers+text',
                    text=lc_ids,
                    textposition="top center",
                    name='Risk vs Return',
                    marker=dict(
                        size=10,
                        color=pl_percentages,
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="P&L %")
                    ),
                    hovertemplate='<b>%{text}</b><br>VaR: %{x:,.0f}<br>P&L: %{y:.1f}%<extra></extra>'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title='Portfolio Risk Management Dashboard',
                height=800,
                showlegend=False,
                template='plotly_white'
            )
            
            # Update axes
            fig.update_xaxes(title_text="LC ID", row=1, col=1)
            fig.update_yaxes(title_text="P&L", row=1, col=1)
            fig.update_xaxes(title_text="Maturity Bucket", row=2, col=1)
            fig.update_yaxes(title_text="Number of LCs", row=2, col=1)
            fig.update_xaxes(title_text="VaR", row=2, col=2)
            fig.update_yaxes(title_text="P&L %", row=2, col=2)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating portfolio dashboard: {e}")
            return self._create_empty_chart("Error creating dashboard")
    
    def create_scenario_analysis_chart(self, scenario_data: List[Dict[str, Any]]) -> go.Figure:
        """
        Create scenario analysis visualization.
        
        Args:
            scenario_data: List of scenario analysis results
        
        Returns:
            Plotly figure object
        """
        try:
            if not scenario_data:
                return self._create_empty_chart("No scenario data available")
            
            # Extract data
            scenario_rates = [s['scenario_rate'] for s in scenario_data]
            scenario_pls = [s['scenario_pl'] for s in scenario_data]
            rate_changes = [s['rate_change_percentage'] for s in scenario_data]
            
            # Create the chart
            fig = go.Figure()
            
            # Add scenario bars
            colors = [self.color_palette['profit'] if pl >= 0 else self.color_palette['loss'] 
                     for pl in scenario_pls]
            
            fig.add_trace(
                go.Bar(
                    x=rate_changes, y=scenario_pls,
                    marker_color=colors,
                    name='Scenario P&L',
                    hovertemplate='<b>Rate Change: %{x:.1f}%</b><br>P&L: %{y:,.0f}<extra></extra>'
                )
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Update layout
            fig.update_layout(
                title='Scenario Analysis: P&L vs Exchange Rate Changes',
                xaxis_title='Exchange Rate Change (%)',
                yaxis_title='Profit/Loss',
                template='plotly_white',
                height=500
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating scenario analysis chart: {e}")
            return self._create_empty_chart("Error creating chart")
    
    def create_risk_metrics_gauge(self, var_percentage: float, 
                                confidence_level: float = 0.95) -> go.Figure:
        """
        Create a gauge chart for risk metrics.
        
        Args:
            var_percentage: VaR percentage
            confidence_level: Confidence level for VaR
        
        Returns:
            Plotly figure object
        """
        try:
            # Determine risk level and color
            if var_percentage < 5:
                risk_level = "Low"
                color = "green"
            elif var_percentage < 15:
                risk_level = "Medium"
                color = "yellow"
            else:
                risk_level = "High"
                color = "red"
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = var_percentage,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Value at Risk ({confidence_level*100:.0f}% Confidence)"},
                delta = {'reference': 10, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                gauge = {
                    'axis': {'range': [None, 30]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 5], 'color': "lightgreen"},
                        {'range': [5, 15], 'color': "yellow"},
                        {'range': [15, 30], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 20
                    }
                }
            ))
            
            fig.update_layout(
                height=400,
                template='plotly_white',
                annotations=[
                    dict(
                        text=f"Risk Level: {risk_level}",
                        x=0.5, y=0.1,
                        showarrow=False,
                        font=dict(size=16, color=color)
                    )
                ]
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating risk gauge: {e}")
            return self._create_empty_chart("Error creating gauge")
    
    def create_currency_correlation_heatmap(self, correlation_data: Dict[str, float]) -> go.Figure:
        """
        Create a correlation heatmap for currency pairs.
        
        Args:
            correlation_data: Dictionary of correlation coefficients
        
        Returns:
            Plotly figure object
        """
        try:
            if not correlation_data:
                return self._create_empty_chart("No correlation data available")
            
            # Parse correlation data into matrix format
            pairs = list(correlation_data.keys())
            currencies = set()
            
            for pair in pairs:
                parts = pair.split('_vs_')
                if len(parts) == 2:
                    for part in parts:
                        # Extract currency from pair string like "USD/INR"
                        curr_pair = part.split('/')
                        currencies.update(curr_pair)
            
            currencies = sorted(list(currencies))
            n_currencies = len(currencies)
            
            if n_currencies < 2:
                return self._create_empty_chart("Insufficient currency data for correlation")
            
            # Create correlation matrix
            correlation_matrix = np.eye(n_currencies)  # Identity matrix as default
            
            # Fill in correlation values
            for pair, corr_value in correlation_data.items():
                parts = pair.split('_vs_')
                if len(parts) == 2:
                    try:
                        curr1 = parts[0].split('/')[0]
                        curr2 = parts[1].split('/')[0]
                        
                        if curr1 in currencies and curr2 in currencies:
                            i = currencies.index(curr1)
                            j = currencies.index(curr2)
                            correlation_matrix[i, j] = corr_value
                            correlation_matrix[j, i] = corr_value
                    except (IndexError, ValueError):
                        continue
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=currencies,
                y=currencies,
                colorscale='RdBu',
                zmid=0,
                colorbar=dict(title="Correlation"),
                hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Currency Correlation Matrix',
                template='plotly_white',
                height=500,
                width=500
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {e}")
            return self._create_empty_chart("Error creating heatmap")
    
    def create_maturity_timeline(self, lcs: List[LetterOfCredit]) -> go.Figure:
        """
        Create a timeline showing LC maturities.
        
        Args:
            lcs: List of Letter of Credit instances
        
        Returns:
            Plotly figure object
        """
        try:
            if not lcs:
                return self._create_empty_chart("No LC data available")
            
            # Prepare data
            lc_ids = []
            signing_dates = []
            maturity_dates = []
            values = []
            colors = []
            
            for lc in lcs:
                lc_ids.append(lc.lc_id)
                signing_dates.append(lc.signing_date_obj)
                maturity_dates.append(lc.maturity_date)
                values.append(lc.total_value)
                
                # Color by days remaining
                if lc.is_matured:
                    colors.append(self.color_palette['neutral'])
                elif lc.days_remaining <= 30:
                    colors.append(self.color_palette['warning'])
                else:
                    colors.append(self.color_palette['profit'])
            
            fig = go.Figure()
            
            # Add timeline bars
            for i, lc_id in enumerate(lc_ids):
                fig.add_trace(
                    go.Scatter(
                        x=[signing_dates[i], maturity_dates[i]],
                        y=[i, i],
                        mode='lines+markers',
                        name=lc_id,
                        line=dict(color=colors[i], width=6),
                        marker=dict(size=8),
                        hovertemplate=f'<b>{lc_id}</b><br>Value: {values[i]:,.0f}<br>%{{x}}<extra></extra>'
                    )
                )
            
            # Add today's line
            today = datetime.now()
            fig.add_vline(x=today, line_dash="dash", line_color="red", 
                         annotation_text="Today")
            
            fig.update_layout(
                title='LC Maturity Timeline',
                xaxis_title='Date',
                yaxis_title='Letter of Credit',
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(lc_ids))),
                    ticktext=lc_ids
                ),
                template='plotly_white',
                height=max(400, len(lc_ids) * 40),
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating maturity timeline: {e}")
            return self._create_empty_chart("Error creating timeline")
    
    def save_chart_as_image(self, fig: go.Figure, filename: str, 
                           format: str = 'png', width: int = 1200, height: int = 800) -> str:
        """
        Save chart as image file.
        
        Args:
            fig: Plotly figure object
            filename: Output filename
            format: Image format ('png', 'jpg', 'svg', 'pdf')
            width: Image width in pixels
            height: Image height in pixels
        
        Returns:
            Path to saved file
        """
        try:
            filepath = f"{filename}.{format}"
            
            if format.lower() == 'png':
                fig.write_image(filepath, format='png', width=width, height=height)
            elif format.lower() == 'jpg':
                fig.write_image(filepath, format='jpeg', width=width, height=height)
            elif format.lower() == 'svg':
                fig.write_image(filepath, format='svg', width=width, height=height)
            elif format.lower() == 'pdf':
                fig.write_image(filepath, format='pdf', width=width, height=height)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Chart saved as {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return ""
    
    def create_interactive_html(self, fig: go.Figure, filename: str) -> str:
        """
        Save chart as interactive HTML file.
        
        Args:
            fig: Plotly figure object
            filename: Output filename
        
        Returns:
            Path to saved HTML file
        """
        try:
            filepath = f"{filename}.html"
            fig.write_html(filepath)
            
            logger.info(f"Interactive chart saved as {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving interactive chart: {e}")
            return ""
    
    def _get_rate_for_date(self, historical_rates: Dict[str, float], 
                          target_date: str) -> Optional[float]:
        """Get rate for a specific date or closest available date."""
        if target_date in historical_rates:
            return historical_rates[target_date]
        
        # Find closest date
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        closest_date = min(
            historical_rates.keys(),
            key=lambda d: abs((datetime.strptime(d, "%Y-%m-%d") - target_dt).days)
        )
        
        return historical_rates[closest_date]
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            height=400,
            showlegend=False
        )
        return fig
