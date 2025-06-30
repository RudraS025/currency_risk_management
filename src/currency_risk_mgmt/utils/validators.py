"""
Data validators for currency risk management system.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates data inputs for currency risk management system.
    """
    
    # Valid currency codes (ISO 4217)
    VALID_CURRENCIES = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
        'INR', 'KRW', 'SGD', 'NOK', 'MXN', 'ZAR', 'TRY', 'BRL', 'RUB', 'PLN',
        'DKK', 'CZK', 'HUF', 'ILS', 'CLP', 'PHP', 'AED', 'SAR', 'THB', 'MYR'
    }
    
    # Valid commodity types
    VALID_COMMODITIES = {
        'Wheat', 'Rice', 'Corn', 'Paddy', 'Barley', 'Oats', 'Soybeans', 'Cotton',
        'Sugar', 'Coffee', 'Cocoa', 'Tea', 'Spices', 'Crude Oil', 'Natural Gas',
        'Gold', 'Silver', 'Copper', 'Iron Ore', 'Coal', 'Steel', 'Aluminum',
        'Other'
    }
    
    # Valid units of measurement
    VALID_UNITS = {
        'tons', 'tonnes', 'kg', 'lbs', 'pounds', 'bushels', 'barrels', 'liters',
        'gallons', 'cubic meters', 'pieces', 'units', 'MT', 'cwt'
    }
    
    # Valid Incoterms
    VALID_INCOTERMS = {
        'EXW', 'FCA', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP', 'FAS', 'FOB', 'CFR', 'CIF'
    }
    
    @staticmethod
    def validate_lc_data(lc_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Letter of Credit data.
        
        Args:
            lc_data: Dictionary containing LC data
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['lc_id', 'commodity', 'quantity', 'unit', 'rate_per_unit', 
                          'currency', 'signing_date', 'maturity_days', 'customer_country']
        
        for field in required_fields:
            if field not in lc_data or lc_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if errors:  # Don't continue if required fields are missing
            return False, errors
        
        # Validate LC ID
        if not DataValidator.validate_lc_id(lc_data['lc_id']):
            errors.append("Invalid LC ID format")
        
        # Validate commodity
        if not DataValidator.validate_commodity(lc_data['commodity']):
            errors.append(f"Invalid commodity: {lc_data['commodity']}")
        
        # Validate quantity
        if not DataValidator.validate_positive_number(lc_data['quantity']):
            errors.append("Quantity must be a positive number")
        
        # Validate unit
        if not DataValidator.validate_unit(lc_data['unit']):
            errors.append(f"Invalid unit: {lc_data['unit']}")
        
        # Validate rate per unit
        if not DataValidator.validate_positive_number(lc_data['rate_per_unit']):
            errors.append("Rate per unit must be a positive number")
        
        # Validate currency
        if not DataValidator.validate_currency(lc_data['currency']):
            errors.append(f"Invalid currency code: {lc_data['currency']}")
        
        # Validate signing date
        if not DataValidator.validate_date_string(lc_data['signing_date']):
            errors.append("Invalid signing date format (expected YYYY-MM-DD)")
        
        # Validate maturity days
        if not DataValidator.validate_positive_integer(lc_data['maturity_days']):
            errors.append("Maturity days must be a positive integer")
        elif lc_data['maturity_days'] > 720:  # 2 years max
            errors.append("Maturity days cannot exceed 720 days")
        
        # Validate customer country
        if not DataValidator.validate_country(lc_data['customer_country']):
            errors.append(f"Invalid customer country: {lc_data['customer_country']}")
        
        # Validate optional Incoterm
        if 'incoterm' in lc_data and lc_data['incoterm']:
            if not DataValidator.validate_incoterm(lc_data['incoterm']):
                errors.append(f"Invalid Incoterm: {lc_data['incoterm']}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_lc_id(lc_id: str) -> bool:
        """
        Validate LC ID format.
        
        Args:
            lc_id: LC ID to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(lc_id, str) or len(lc_id) < 3:
            return False
        
        # Allow alphanumeric with dashes, underscores
        pattern = r'^[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, lc_id))
    
    @staticmethod
    def validate_currency(currency: str) -> bool:
        """
        Validate currency code.
        
        Args:
            currency: Currency code to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(currency, str):
            return False
        
        return currency.upper() in DataValidator.VALID_CURRENCIES
    
    @staticmethod
    def validate_commodity(commodity: str) -> bool:
        """
        Validate commodity type.
        
        Args:
            commodity: Commodity to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(commodity, str) or len(commodity) < 2:
            return False
        
        # Allow any reasonable commodity name (not just from predefined list)
        # Check for basic sanity (no special characters except spaces and hyphens)
        pattern = r'^[A-Za-z0-9\s\-_]+$'
        return bool(re.match(pattern, commodity))
    
    @staticmethod
    def validate_unit(unit: str) -> bool:
        """
        Validate unit of measurement.
        
        Args:
            unit: Unit to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(unit, str):
            return False
        
        # Allow common units (case insensitive)
        return unit.lower() in [u.lower() for u in DataValidator.VALID_UNITS] or \
               bool(re.match(r'^[A-Za-z]+$', unit))
    
    @staticmethod
    def validate_incoterm(incoterm: str) -> bool:
        """
        Validate Incoterm.
        
        Args:
            incoterm: Incoterm to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(incoterm, str):
            return False
        
        return incoterm.upper() in DataValidator.VALID_INCOTERMS
    
    @staticmethod
    def validate_country(country: str) -> bool:
        """
        Validate country name.
        
        Args:
            country: Country name to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(country, str) or len(country) < 2:
            return False
        
        # Basic validation for country name
        pattern = r'^[A-Za-z\s\-\'\.]+$'
        return bool(re.match(pattern, country)) and len(country) <= 50
    
    @staticmethod
    def validate_positive_number(value: Any) -> bool:
        """
        Validate that a value is a positive number.
        
        Args:
            value: Value to validate
        
        Returns:
            True if valid positive number, False otherwise
        """
        try:
            num = float(value)
            return num > 0 and not (isinstance(num, float) and (num != num or num == float('inf')))
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_positive_integer(value: Any) -> bool:
        """
        Validate that a value is a positive integer.
        
        Args:
            value: Value to validate
        
        Returns:
            True if valid positive integer, False otherwise
        """
        try:
            num = int(value)
            return num > 0 and num == float(value)  # Ensure it's actually an integer
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_string(date_str: str) -> bool:
        """
        Validate date string in YYYY-MM-DD format.
        
        Args:
            date_str: Date string to validate
        
        Returns:
            True if valid date, False otherwise
        """
        if not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_exchange_rate(rate: Any) -> bool:
        """
        Validate exchange rate.
        
        Args:
            rate: Exchange rate to validate
        
        Returns:
            True if valid rate, False otherwise
        """
        try:
            rate_float = float(rate)
            return 0 < rate_float < 10000  # Reasonable range for exchange rates
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_percentage(percentage: Any) -> bool:
        """
        Validate percentage value.
        
        Args:
            percentage: Percentage to validate
        
        Returns:
            True if valid percentage, False otherwise
        """
        try:
            pct = float(percentage)
            return -100 <= pct <= 100  # Allow negative percentages for losses
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address.
        
        Args:
            email: Email to validate
        
        Returns:
            True if valid email, False otherwise
        """
        if not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number (basic international format).
        
        Args:
            phone: Phone number to validate
        
        Returns:
            True if valid phone number, False otherwise
        """
        if not isinstance(phone, str):
            return False
        
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check for + at start and digits
        pattern = r'^\+?[1-9]\d{6,14}$'
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """
        Sanitize string input.
        
        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return ""
        
        # Remove leading/trailing whitespace
        sanitized = input_str.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate JSON structure has required keys.
        
        Args:
            data: Dictionary to validate
            required_keys: List of required keys
        
        Returns:
            Tuple of (is_valid, list_of_missing_keys)
        """
        if not isinstance(data, dict):
            return False, ["Input is not a dictionary"]
        
        missing_keys = [key for key in required_keys if key not in data]
        
        return len(missing_keys) == 0, missing_keys
    
    @staticmethod
    def validate_api_response(response_data: Dict[str, Any]) -> bool:
        """
        Validate API response structure.
        
        Args:
            response_data: API response to validate
        
        Returns:
            True if valid response, False otherwise
        """
        if not isinstance(response_data, dict):
            return False
        
        # Check for common error indicators
        if 'error' in response_data and response_data['error']:
            logger.warning(f"API response contains error: {response_data.get('error')}")
            return False
        
        if 'status' in response_data and response_data['status'] in ['error', 'failed']:
            logger.warning(f"API response status indicates failure: {response_data.get('status')}")
            return False
        
        return True
    
    @staticmethod
    def validate_risk_parameters(confidence_level: float, time_horizon: int) -> Tuple[bool, List[str]]:
        """
        Validate risk calculation parameters.
        
        Args:
            confidence_level: Confidence level (e.g., 0.95)
            time_horizon: Time horizon in days
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(confidence_level, (int, float)):
            errors.append("Confidence level must be a number")
        elif not 0.5 <= confidence_level <= 0.999:
            errors.append("Confidence level must be between 0.5 and 0.999")
        
        if not isinstance(time_horizon, int):
            errors.append("Time horizon must be an integer")
        elif not 1 <= time_horizon <= 365:
            errors.append("Time horizon must be between 1 and 365 days")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_validation_summary(cls) -> Dict[str, Any]:
        """
        Get summary of validation rules and supported values.
        
        Returns:
            Dictionary containing validation rules summary
        """
        return {
            'supported_currencies': sorted(list(cls.VALID_CURRENCIES)),
            'supported_commodities': sorted(list(cls.VALID_COMMODITIES)),
            'supported_units': sorted(list(cls.VALID_UNITS)),
            'supported_incoterms': sorted(list(cls.VALID_INCOTERMS)),
            'date_format': 'YYYY-MM-DD',
            'max_maturity_days': 720,
            'exchange_rate_range': '0 to 10,000',
            'percentage_range': '-100% to +100%'
        }
