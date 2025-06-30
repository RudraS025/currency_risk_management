"""
Date utilities for currency risk management system.
"""

from datetime import datetime, timedelta, date
from typing import List, Optional, Tuple
import calendar
import logging

logger = logging.getLogger(__name__)


class DateUtils:
    """
    Utility class for date-related operations in currency risk management.
    """
    
    @staticmethod
    def is_business_day(date_obj: datetime) -> bool:
        """
        Check if a given date is a business day (Monday-Friday).
        
        Args:
            date_obj: Date to check
        
        Returns:
            True if business day, False otherwise
        """
        return date_obj.weekday() < 5
    
    @staticmethod
    def get_next_business_day(date_obj: datetime) -> datetime:
        """
        Get the next business day after the given date.
        
        Args:
            date_obj: Starting date
        
        Returns:
            Next business day
        """
        next_day = date_obj + timedelta(days=1)
        while not DateUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    @staticmethod
    def get_previous_business_day(date_obj: datetime) -> datetime:
        """
        Get the previous business day before the given date.
        
        Args:
            date_obj: Starting date
        
        Returns:
            Previous business day
        """
        prev_day = date_obj - timedelta(days=1)
        while not DateUtils.is_business_day(prev_day):
            prev_day -= timedelta(days=1)
        return prev_day
    
    @staticmethod
    def count_business_days(start_date: datetime, end_date: datetime) -> int:
        """
        Count business days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Number of business days
        """
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if DateUtils.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def add_business_days(start_date: datetime, business_days: int) -> datetime:
        """
        Add business days to a date.
        
        Args:
            start_date: Starting date
            business_days: Number of business days to add
        
        Returns:
            Resulting date
        """
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if DateUtils.is_business_day(current_date):
                days_added += 1
        
        return current_date
    
    @staticmethod
    def get_month_end_date(year: int, month: int) -> datetime:
        """
        Get the last day of a given month.
        
        Args:
            year: Year
            month: Month (1-12)
        
        Returns:
            Last day of the month
        """
        last_day = calendar.monthrange(year, month)[1]
        return datetime(year, month, last_day)
    
    @staticmethod
    def get_quarter_dates(year: int, quarter: int) -> Tuple[datetime, datetime]:
        """
        Get start and end dates for a quarter.
        
        Args:
            year: Year
            quarter: Quarter (1-4)
        
        Returns:
            Tuple of (start_date, end_date)
        """
        if quarter not in [1, 2, 3, 4]:
            raise ValueError("Quarter must be 1, 2, 3, or 4")
        
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        
        start_date = datetime(year, start_month, 1)
        end_date = DateUtils.get_month_end_date(year, end_month)
        
        return start_date, end_date
    
    @staticmethod
    def get_maturity_buckets(dates: List[datetime], 
                           reference_date: Optional[datetime] = None) -> dict:
        """
        Categorize dates into maturity buckets.
        
        Args:
            dates: List of dates to categorize
            reference_date: Reference date (default: today)
        
        Returns:
            Dictionary with bucket counts
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        buckets = {
            '0-7 days': 0,
            '8-30 days': 0,
            '31-60 days': 0,
            '61-90 days': 0,
            '91-180 days': 0,
            '181+ days': 0,
            'past_due': 0
        }
        
        for date_obj in dates:
            days_diff = (date_obj - reference_date).days
            
            if days_diff < 0:
                buckets['past_due'] += 1
            elif days_diff <= 7:
                buckets['0-7 days'] += 1
            elif days_diff <= 30:
                buckets['8-30 days'] += 1
            elif days_diff <= 60:
                buckets['31-60 days'] += 1
            elif days_diff <= 90:
                buckets['61-90 days'] += 1
            elif days_diff <= 180:
                buckets['91-180 days'] += 1
            else:
                buckets['181+ days'] += 1
        
        return buckets
    
    @staticmethod
    def is_forex_market_open(date_obj: datetime) -> bool:
        """
        Check if forex market is likely open at the given date/time.
        Note: This is a simplified check. Real implementation would consider holidays.
        
        Args:
            date_obj: Date and time to check
        
        Returns:
            True if market likely open, False otherwise
        """
        # Forex market is open 24/5 (Monday-Friday)
        weekday = date_obj.weekday()
        
        # Closed on weekends
        if weekday >= 5:  # Saturday or Sunday
            return False
        
        # Simple check - market opens Monday morning, closes Friday evening
        if weekday == 0:  # Monday
            return date_obj.hour >= 0  # Opens at midnight Monday
        elif weekday == 4:  # Friday
            return date_obj.hour < 22  # Closes at 10 PM Friday
        else:  # Tuesday-Thursday
            return True
    
    @staticmethod
    def get_forex_market_hours(date_obj: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get forex market opening and closing times for a given date.
        
        Args:
            date_obj: Date to check
        
        Returns:
            Tuple of (market_open, market_close) or (None, None) if closed
        """
        weekday = date_obj.weekday()
        
        if weekday >= 5:  # Weekend
            return None, None
        
        date_only = date_obj.date()
        
        if weekday == 0:  # Monday
            market_open = datetime.combine(date_only, datetime.min.time())
            market_close = datetime.combine(date_only, datetime.max.time())
        elif weekday == 4:  # Friday
            market_open = datetime.combine(date_only, datetime.min.time())
            market_close = datetime.combine(date_only, datetime.min.time().replace(hour=22))
        else:  # Tuesday-Thursday
            market_open = datetime.combine(date_only, datetime.min.time())
            market_close = datetime.combine(date_only, datetime.max.time())
        
        return market_open, market_close
    
    @staticmethod
    def calculate_days_360(start_date: datetime, end_date: datetime) -> int:
        """
        Calculate days using 360-day year convention (30/360).
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Days using 360-day convention
        """
        start_day = min(start_date.day, 30)
        end_day = min(end_date.day, 30) if start_day == 30 else end_date.day
        
        days = (end_date.year - start_date.year) * 360 + \
               (end_date.month - start_date.month) * 30 + \
               (end_day - start_day)
        
        return days
    
    @staticmethod
    def get_date_range_list(start_date: datetime, end_date: datetime, 
                           interval_days: int = 1) -> List[datetime]:
        """
        Generate a list of dates between start and end date.
        
        Args:
            start_date: Start date
            end_date: End date
            interval_days: Interval between dates in days
        
        Returns:
            List of datetime objects
        """
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=interval_days)
        
        return dates
    
    @staticmethod
    def format_date_for_api(date_obj: datetime, format_type: str = "iso") -> str:
        """
        Format date for API calls.
        
        Args:
            date_obj: Date to format
            format_type: Format type ('iso', 'us', 'uk', 'compact')
        
        Returns:
            Formatted date string
        """
        if format_type == "iso":
            return date_obj.strftime("%Y-%m-%d")
        elif format_type == "us":
            return date_obj.strftime("%m/%d/%Y")
        elif format_type == "uk":
            return date_obj.strftime("%d/%m/%Y")
        elif format_type == "compact":
            return date_obj.strftime("%Y%m%d")
        else:
            return date_obj.strftime("%Y-%m-%d")
    
    @staticmethod
    def parse_flexible_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
        
        Returns:
            Parsed datetime object or None if parsing fails
        """
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%Y%m%d",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date string: {date_str}")
        return None
    
    @staticmethod
    def get_relative_date_description(date_obj: datetime, 
                                    reference_date: Optional[datetime] = None) -> str:
        """
        Get a human-readable description of a date relative to reference date.
        
        Args:
            date_obj: Date to describe
            reference_date: Reference date (default: today)
        
        Returns:
            Human-readable description
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        days_diff = (date_obj - reference_date).days
        
        if days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Tomorrow"
        elif days_diff == -1:
            return "Yesterday"
        elif days_diff > 0:
            if days_diff <= 7:
                return f"In {days_diff} days"
            elif days_diff <= 30:
                weeks = days_diff // 7
                return f"In {weeks} week{'s' if weeks > 1 else ''}"
            elif days_diff <= 365:
                months = days_diff // 30
                return f"In {months} month{'s' if months > 1 else ''}"
            else:
                years = days_diff // 365
                return f"In {years} year{'s' if years > 1 else ''}"
        else:
            days_diff = abs(days_diff)
            if days_diff <= 7:
                return f"{days_diff} days ago"
            elif days_diff <= 30:
                weeks = days_diff // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif days_diff <= 365:
                months = days_diff // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = days_diff // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
