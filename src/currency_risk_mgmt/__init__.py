"""
Currency Risk Management System

A comprehensive software solution for managing currency risk in international trade transactions.
"""

from .models.letter_of_credit import LetterOfCredit
from .models.transaction import Transaction
from .data_providers.forex_provider import ForexDataProvider
from .calculators.profit_loss import ProfitLossCalculator
from .calculators.risk_metrics import RiskMetricsCalculator
from .reports.generator import ReportGenerator

__version__ = "1.0.0"
__author__ = "Currency Risk Management Team"

__all__ = [
    "LetterOfCredit",
    "Transaction",
    "ForexDataProvider",
    "ProfitLossCalculator",
    "RiskMetricsCalculator",
    "ReportGenerator"
]
