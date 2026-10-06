"""
Utility helper functions for the Smart Canteen Management System.
Provides formatting, validation, and calculation utilities.
"""

from typing import Any, Dict, List


def format_currency(amount: float) -> str:
    """Format numerical amount into standard USD currency string ($X.XX)."""
    if amount is None:
        return "$0.00"
    return f"${float(amount):.2f}"


def validate_user_identifier(user_id: str) -> bool:
    """
    Validate that user/student ID follows canteen requirements:
    - Non-empty string
    - Minimum length 3
    - Contains only alphanumeric characters, dashes, and underscores
    """
    if not isinstance(user_id, str):
        return False
    trimmed = user_id.strip()
    if len(trimmed) < 3:
        return False
    return trimmed.replace("-", "").replace("_", "").isalnum()


def is_low_stock(stock_quantity: int, stock_threshold: int) -> bool:
    """Check if stock level has reached or dropped below alert threshold."""
    if stock_quantity is None or stock_threshold is None:
        return False
    return int(stock_quantity) <= int(stock_threshold)


def calculate_order_subtotal(items: List[Dict[str, Any]]) -> float:
    """
    Calculate total cost for a list of order items containing price and quantity.
    Returns float rounded to 2 decimal places.
    """
    if not items:
        return 0.0
    total = sum(
        float(item.get("price", 0.0)) * int(item.get("quantity", 1))
        for item in items
    )
    return round(total, 2)


def sanitize_item_name(name: str) -> str:
    """Clean and standardize food item name input."""
    if not name or not isinstance(name, str):
        return ""
    # Normalize excessive spaces
    cleaned = " ".join(name.strip().split())
    return cleaned
