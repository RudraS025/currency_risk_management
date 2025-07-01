"""
Letter of Credit model for currency risk management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LetterOfCredit:
    """
    Represents a Letter of Credit for international trade transactions.
    
    Attributes:
        lc_id: Unique identifier for the LC
        commodity: Type of commodity being traded
        quantity: Quantity of commodity
        unit: Unit of measurement (tons, kg, etc.)
        rate_per_unit: Price per unit in the specified currency
        currency: Currency of the transaction (e.g., 'USD')
        signing_date: Date when LC was signed
        maturity_days: Number of days until LC maturity
        customer_country: Country of the importing customer
        contract_rate: Exchange rate (USD/INR) at the time of signing
        incoterm: International commercial term (FOB, CIF, etc.)
        port_of_loading: Port where goods will be loaded
        port_of_discharge: Port where goods will be discharged
        description: Additional description of the transaction
    """
    
    lc_id: str
    commodity: str
    quantity: float
    unit: str
    rate_per_unit: float
    currency: str
    signing_date: str  # Format: YYYY-MM-DD
    maturity_days: int
    customer_country: str
    contract_rate: float = 84.15  # USD/INR exchange rate at signing (default current rate)
    incoterm: str = "FOB"
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate and process the LC data after initialization."""
        self._validate_data()
        self._signing_date = datetime.strptime(self.signing_date, "%Y-%m-%d")
        self._maturity_date = self._signing_date + timedelta(days=self.maturity_days)
        
        logger.info(f"Created LC {self.lc_id} for {self.quantity} {self.unit} of {self.commodity}")
    
    def _validate_data(self):
        """Validate the LC data."""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.rate_per_unit <= 0:
            raise ValueError("Rate per unit must be positive")
        
        if self.maturity_days <= 0:
            raise ValueError("Maturity days must be positive")
        
        # Validate date format
        try:
            datetime.strptime(self.signing_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Signing date must be in YYYY-MM-DD format")
        
        # Validate currency
        if self.currency not in ['USD', 'EUR', 'GBP', 'JPY']:
            logger.warning(f"Currency {self.currency} may not be supported by all data providers")
    
    @property
    def total_value(self) -> float:
        """Calculate total value of the LC in the transaction currency."""
        return self.quantity * self.rate_per_unit
    
    @property
    def signing_date_obj(self) -> datetime:
        """Get signing date as datetime object."""
        return self._signing_date
    
    @property
    def issue_date(self) -> datetime:
        """Get issue date as datetime object (alias for signing_date_obj)."""
        return self._signing_date
    
    @property
    def maturity_date(self) -> datetime:
        """Get maturity date as datetime object."""
        return self._maturity_date
    
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining until maturity."""
        today = datetime.now()
        if today >= self._maturity_date:
            return 0
        return (self._maturity_date - today).days
    
    @property
    def days_elapsed(self) -> int:
        """Calculate days elapsed since signing."""
        today = datetime.now()
        if today <= self._signing_date:
            return 0
        return (today - self._signing_date).days
    
    @property
    def is_matured(self) -> bool:
        """Check if the LC has matured."""
        return datetime.now() >= self._maturity_date
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage from signing to maturity."""
        if self.is_matured:
            return 100.0
        
        total_days = self.maturity_days
        elapsed_days = self.days_elapsed
        
        return min((elapsed_days / total_days) * 100, 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert LC to dictionary for serialization."""
        return {
            'lc_id': self.lc_id,
            'commodity': self.commodity,
            'quantity': self.quantity,
            'unit': self.unit,
            'rate_per_unit': self.rate_per_unit,
            'currency': self.currency,
            'signing_date': self.signing_date,
            'maturity_days': self.maturity_days,
            'customer_country': self.customer_country,
            'contract_rate': self.contract_rate,
            'incoterm': self.incoterm,
            'port_of_loading': self.port_of_loading,
            'port_of_discharge': self.port_of_discharge,
            'description': self.description,
            'total_value': self.total_value,
            'maturity_date': self.maturity_date.strftime("%Y-%m-%d"),
            'days_remaining': self.days_remaining,
            'days_elapsed': self.days_elapsed,
            'is_matured': self.is_matured,
            'progress_percentage': self.get_progress_percentage()
        }
    
    def __str__(self) -> str:
        """String representation of the LC."""
        return (f"LC {self.lc_id}: {self.quantity} {self.unit} {self.commodity} "
                f"@ {self.currency} {self.rate_per_unit}/{self.unit} "
                f"(Total: {self.currency} {self.total_value:,.2f})")
    
    def __repr__(self) -> str:
        """Detailed representation of the LC."""
        return (f"LetterOfCredit(lc_id='{self.lc_id}', commodity='{self.commodity}', "
                f"quantity={self.quantity}, unit='{self.unit}', "
                f"rate_per_unit={self.rate_per_unit}, currency='{self.currency}', "
                f"signing_date='{self.signing_date}', maturity_days={self.maturity_days})")
