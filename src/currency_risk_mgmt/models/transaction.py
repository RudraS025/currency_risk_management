"""
Transaction model for recording financial transactions.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of transactions in the system."""
    LC_CREATION = "lc_creation"
    FOREX_HEDGING = "forex_hedging"
    PAYMENT_RECEIVED = "payment_received"
    SETTLEMENT = "settlement"
    ADJUSTMENT = "adjustment"


class TransactionStatus(Enum):
    """Status of transactions."""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Transaction:
    """
    Represents a financial transaction related to currency risk management.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        lc_id: Related Letter of Credit ID
        transaction_type: Type of transaction
        amount: Transaction amount
        currency: Currency of the transaction
        exchange_rate: Exchange rate used (if applicable)
        transaction_date: Date of the transaction
        description: Description of the transaction
        status: Current status of the transaction
        reference_id: External reference ID (bank reference, etc.)
        counterparty: Name of the counterparty
        created_at: When the transaction record was created
        updated_at: When the transaction record was last updated
    """
    
    transaction_id: str
    lc_id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    transaction_date: str  # Format: YYYY-MM-DD
    description: str
    status: TransactionStatus = TransactionStatus.PENDING
    exchange_rate: Optional[float] = None
    reference_id: Optional[str] = None
    counterparty: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Process the transaction data after initialization."""
        self._validate_data()
        self._transaction_date = datetime.strptime(self.transaction_date, "%Y-%m-%d")
        
        # Set timestamps if not provided
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        
        logger.info(f"Created transaction {self.transaction_id} for LC {self.lc_id}")
    
    def _validate_data(self):
        """Validate the transaction data."""
        if self.amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        
        # Validate date format
        try:
            datetime.strptime(self.transaction_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Transaction date must be in YYYY-MM-DD format")
        
        # Validate exchange rate if provided
        if self.exchange_rate is not None and self.exchange_rate <= 0:
            raise ValueError("Exchange rate must be positive")
    
    @property
    def transaction_date_obj(self) -> datetime:
        """Get transaction date as datetime object."""
        return self._transaction_date
    
    @property
    def is_completed(self) -> bool:
        """Check if the transaction is completed."""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_pending(self) -> bool:
        """Check if the transaction is pending."""
        return self.status == TransactionStatus.PENDING
    
    @property
    def inr_equivalent(self) -> Optional[float]:
        """Calculate INR equivalent if exchange rate is available."""
        if self.exchange_rate is None:
            return None
        
        if self.currency == 'INR':
            return self.amount
        elif self.currency == 'USD':
            return self.amount * self.exchange_rate
        else:
            # For other currencies, would need appropriate conversion
            logger.warning(f"INR conversion not implemented for {self.currency}")
            return None
    
    def update_status(self, new_status: TransactionStatus, description: Optional[str] = None):
        """Update the transaction status."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now().isoformat()
        
        if description:
            self.description += f" | Status update: {description}"
        
        logger.info(f"Transaction {self.transaction_id} status changed from {old_status.value} to {new_status.value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for serialization."""
        return {
            'transaction_id': self.transaction_id,
            'lc_id': self.lc_id,
            'transaction_type': self.transaction_type.value,
            'amount': self.amount,
            'currency': self.currency,
            'exchange_rate': self.exchange_rate,
            'transaction_date': self.transaction_date,
            'description': self.description,
            'status': self.status.value,
            'reference_id': self.reference_id,
            'counterparty': self.counterparty,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_completed': self.is_completed,
            'is_pending': self.is_pending,
            'inr_equivalent': self.inr_equivalent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        # Convert string enums back to enum objects
        if isinstance(data.get('transaction_type'), str):
            data['transaction_type'] = TransactionType(data['transaction_type'])
        
        if isinstance(data.get('status'), str):
            data['status'] = TransactionStatus(data['status'])
        
        # Remove computed fields
        computed_fields = ['is_completed', 'is_pending', 'inr_equivalent']
        for field in computed_fields:
            data.pop(field, None)
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of the transaction."""
        return (f"Transaction {self.transaction_id}: {self.transaction_type.value} "
                f"{self.currency} {self.amount:,.2f} ({self.status.value})")
    
    def __repr__(self) -> str:
        """Detailed representation of the transaction."""
        return (f"Transaction(transaction_id='{self.transaction_id}', "
                f"lc_id='{self.lc_id}', transaction_type={self.transaction_type}, "
                f"amount={self.amount}, currency='{self.currency}', "
                f"status={self.status})")
