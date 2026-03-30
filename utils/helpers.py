"""Helper functions module."""

from datetime import datetime
from typing import Union, Optional
from utils.logger import Logger


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default on division by zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if denominator is zero

    Returns:
        Division result or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def validate_stock_symbol(symbol: str) -> Optional[str]:
    """Validate stock symbol format.

    Args:
        symbol: Stock symbol to validate

    Returns:
        Validated symbol or None if invalid
    """
    if not symbol or not isinstance(symbol, str):
        return None

    # Remove whitespace
    symbol = symbol.strip()

    # Check minimum length
    if len(symbol) < 6:
        return None

    # Validate format (6 digits + optional exchange suffix)
    import re
    if not re.match(r'^\d{6}(\.(SH|SZ))?$', symbol):
        return None

    return symbol


def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message for user display.

    Args:
        error: Exception object
        context: Additional context about where the error occurred

    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        return f"{context}: {error_type} - {error_msg}"
    return f"{error_type}: {error_msg}"


def format_date(date: Union[str, datetime]) -> str:
    """Format date to YYYY-MM-DD string.

    Args:
        date: Date as string or datetime object

    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        return date
    return date.strftime('%Y-%m-%d')

def format_price(price: float) -> str:
    """Format price to 2 decimal places.

    Args:
        price: Price value

    Returns:
        Formatted price string
    """
    return f"{price:.2f}"

def format_volume(volume: float) -> str:
    """Format volume with units.

    Args:
        volume: Volume value

    Returns:
        Formatted volume string with unit
    """
    if volume is None or volume < 0:
        return "0"

    if volume >= 100000000:  # 亿
        return f"{volume / 100000000:.2f}亿"
    elif volume >= 10000:  # 万
        return f"{volume / 10000:.2f}万"
    else:
        return f"{volume:.0f}"

def calculate_return(start_price: float, end_price: float) -> float:
    """Calculate return rate.

    Args:
        start_price: Starting price
        end_price: Ending price

    Returns:
        Return rate (e.g., 0.1 for 10%)
    """
    if start_price is None or end_price is None:
        return 0.0
    if start_price == 0:
        return 0.0
    return (end_price - start_price) / start_price

def action_to_chinese(action: str) -> str:
    """Convert action to Chinese.

    Args:
        action: Action ('buy', 'sell', 'hold')

    Returns:
        Chinese text for the action
    """
    mapping = {
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有'
    }
    return mapping.get(action, action)

def color_for_action(action: str) -> str:
    """Get color for an action (Chinese stock market: red = up, green = down).

    Args:
        action: Action ('buy', 'sell', 'hold')

    Returns:
        Color name
    """
    mapping = {
        'buy': 'red',
        'sell': 'green',
        'hold': 'gray'
    }
    return mapping.get(action, 'gray')