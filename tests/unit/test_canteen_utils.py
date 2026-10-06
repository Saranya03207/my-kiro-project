"""
Unit tests for canteen utility functions in backend.utils.helpers.
Validates currency formatting, user ID validation, stock threshold evaluation,
subtotal calculations, and item name sanitization.
"""

import pytest
from backend.utils.helpers import (
    format_currency,
    validate_user_identifier,
    is_low_stock,
    calculate_order_subtotal,
    sanitize_item_name,
)


class TestFormatCurrency:
    """Test suite for format_currency utility."""

    def test_format_zero(self):
        assert format_currency(0) == "$0.00"
        assert format_currency(0.0) == "$0.00"

    def test_format_standard_amounts(self):
        assert format_currency(5.5) == "$5.50"
        assert format_currency(12.99) == "$12.99"
        assert format_currency(100) == "$100.00"

    def test_format_rounding(self):
        assert format_currency(4.556) == "$4.56"
        assert format_currency(4.554) == "$4.55"

    def test_format_none_fallback(self):
        assert format_currency(None) == "$0.00"


class TestValidateUserIdentifier:
    """Test suite for validate_user_identifier utility."""

    def test_valid_ids(self):
        assert validate_user_identifier("S001") is True
        assert validate_user_identifier("admin001") is True
        assert validate_user_identifier("student-42") is True
        assert validate_user_identifier("user_99") is True

    def test_short_ids(self):
        assert validate_user_identifier("") is False
        assert validate_user_identifier("ab") is False
        assert validate_user_identifier("12") is False

    def test_invalid_characters(self):
        assert validate_user_identifier("S001!") is False
        assert validate_user_identifier("user@domain") is False
        assert validate_user_identifier("user name") is False

    def test_non_string_types(self):
        assert validate_user_identifier(None) is False
        assert validate_user_identifier(12345) is False


class TestIsLowStock:
    """Test suite for is_low_stock utility."""

    def test_stock_below_threshold(self):
        assert is_low_stock(2, 5) is True
        assert is_low_stock(0, 3) is True

    def test_stock_equal_threshold(self):
        assert is_low_stock(5, 5) is True
        assert is_low_stock(0, 0) is True

    def test_stock_above_threshold(self):
        assert is_low_stock(10, 5) is False
        assert is_low_stock(6, 5) is False

    def test_none_arguments(self):
        assert is_low_stock(None, 5) is False
        assert is_low_stock(5, None) is False


class TestCalculateOrderSubtotal:
    """Test suite for calculate_order_subtotal utility."""

    def test_empty_list(self):
        assert calculate_order_subtotal([]) == 0.0

    def test_single_item(self):
        items = [{"price": 7.50, "quantity": 2}]
        assert calculate_order_subtotal(items) == 15.00

    def test_multiple_items(self):
        items = [
            {"price": 4.99, "quantity": 1},
            {"price": 2.50, "quantity": 3},
            {"price": 10.00, "quantity": 2},
        ]
        # 4.99 + 7.50 + 20.00 = 32.49
        assert calculate_order_subtotal(items) == 32.49

    def test_missing_price_or_quantity_defaults(self):
        items = [{"quantity": 2}, {"price": 3.00}]
        # 0.0 * 2 + 3.00 * 1 = 3.00
        assert calculate_order_subtotal(items) == 3.00


class TestSanitizeItemName:
    """Test suite for sanitize_item_name utility."""

    def test_normal_string(self):
        assert sanitize_item_name("Veg Biryani") == "Veg Biryani"

    def test_whitespace_stripping(self):
        assert sanitize_item_name("   Masala Dosa   ") == "Masala Dosa"
        assert sanitize_item_name("Cold   Coffee   Special") == "Cold Coffee Special"

    def test_empty_or_invalid_inputs(self):
        assert sanitize_item_name("") == ""
        assert sanitize_item_name("   ") == ""
        assert sanitize_item_name(None) == ""
