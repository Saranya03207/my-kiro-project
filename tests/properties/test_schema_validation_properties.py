"""
Property-based tests for schema validation.
Tests Pydantic schema validation rules using Hypothesis.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from decimal import Decimal
from pydantic import ValidationError

from backend.schemas.order import OrderCreate, OrderItemCreate
from backend.schemas.menu_item import MenuItemCreate, MenuItemUpdate


# Feature: smart-canteen-manager, Property 8: Order Item Quantity Validation
@given(
    menu_item_id=st.integers(),
    quantity=st.integers()
)
@settings(max_examples=100)
def test_order_item_quantity_must_be_positive(menu_item_id, quantity):
    """
    Property: OrderItemCreate quantity must be >= 1.
    Validates: Requirements 8.5, 15.4
    
    For any order item with quantity Q, Q SHALL be >= 1.
    """
    is_valid_id = menu_item_id > 0
    is_valid_quantity = quantity >= 1
    
    if is_valid_id and is_valid_quantity:
        # Valid inputs should create successful order item
        order_item = OrderItemCreate(
            menu_item_id=menu_item_id,
            quantity=quantity
        )
        assert order_item.menu_item_id == menu_item_id
        assert order_item.quantity == quantity
    else:
        # Invalid inputs should raise ValidationError
        with pytest.raises(ValidationError):
            OrderItemCreate(
                menu_item_id=menu_item_id,
                quantity=quantity
            )


# Feature: smart-canteen-manager, Property 9: Order Must Contain Items
@given(
    items_list=st.lists(
        st.builds(
            OrderItemCreate,
            menu_item_id=st.integers(min_value=1, max_value=1000),
            quantity=st.integers(min_value=1, max_value=20)
        ),
        min_size=0,
        max_size=50
    )
)
@settings(max_examples=100)
def test_order_must_contain_at_least_one_item(items_list):
    """
    Property: OrderCreate must contain at least one item.
    Validates: Requirements 8.6, 15.1
    
    For any order O, O.items SHALL have length >= 1.
    """
    has_items = len(items_list) > 0
    
    if has_items:
        # Order with items should be valid
        order = OrderCreate(items=items_list)
        assert len(order.items) == len(items_list)
        assert len(order.items) >= 1
    else:
        # Empty order should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(items=items_list)
        
        error_message = str(exc_info.value)
        assert "at least 1 item" in error_message.lower()


# Feature: smart-canteen-manager, Property 10: Menu Item Name Length Validation
@given(
    name=st.text(),
    description=st.text(min_size=1, max_size=500),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2),
    category=st.text(min_size=1, max_size=50),
    stock_quantity=st.integers(min_value=0, max_value=1000),
    stock_threshold=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_menu_item_name_length_constraints(name, description, price, category, stock_quantity, stock_threshold):
    """
    Property: Menu item name must be 1-100 characters and not empty/whitespace.
    Validates: Requirements 7.1, 17.1
    
    For any menu item name N:
    - 1 <= len(N.strip()) <= 100
    - N.strip() must not be empty
    """
    is_valid_name = 1 <= len(name.strip()) <= 100 and name.strip()
    is_valid_category = 1 <= len(category.strip()) <= 50 and category.strip()
    is_valid_description = 1 <= len(description.strip()) <= 500 and description.strip()
    
    if is_valid_name and is_valid_category and is_valid_description:
        # Valid name should allow menu item creation
        menu_item = MenuItemCreate(
            name=name,
            description=description,
            price=price,
            category=category,
            stock_quantity=stock_quantity,
            stock_threshold=stock_threshold
        )
        assert menu_item.name == name.strip()
        assert len(menu_item.name) >= 1
        assert len(menu_item.name) <= 100
    else:
        # Invalid name should raise ValidationError
        with pytest.raises(ValidationError):
            MenuItemCreate(
                name=name,
                description=description,
                price=price,
                category=category,
                stock_quantity=stock_quantity,
                stock_threshold=stock_threshold
            )


# Feature: smart-canteen-manager, Property 11: Price Decimal Places Validation
@given(
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Zs'))),
    description=st.text(min_size=1, max_size=200),
    price=st.decimals(min_value=Decimal("-999.99"), max_value=Decimal("99999.999"), places=None),
    category=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    stock_quantity=st.integers(min_value=0, max_value=1000),
    stock_threshold=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_menu_item_price_decimal_places_validation(name, description, price, category, stock_quantity, stock_threshold):
    """
    Property: Menu item price must be >= 0.01 and have at most 2 decimal places.
    Validates: Requirements 7.4, 17.5
    
    For any price P:
    - P >= 0.01
    - P <= 9999.99  
    - P has at most 2 decimal places
    """
    assume(name.strip() and description.strip() and category.strip())
    
    # Determine if price meets validation criteria
    decimal_places = abs(price.as_tuple().exponent) if price.as_tuple().exponent < 0 else 0
    is_valid_price = (
        price >= Decimal("0.01") and 
        price <= Decimal("9999.99") and
        decimal_places <= 2
    )
    
    if is_valid_price:
        # Valid price should allow menu item creation
        menu_item = MenuItemCreate(
            name=name,
            description=description,
            price=price,
            category=category,
            stock_quantity=stock_quantity,
            stock_threshold=stock_threshold
        )
        assert menu_item.price == price
        assert menu_item.price >= Decimal("0.01")
        assert menu_item.price <= Decimal("9999.99")
        
        # Verify decimal places constraint
        result_decimal_places = abs(menu_item.price.as_tuple().exponent) if menu_item.price.as_tuple().exponent < 0 else 0
        assert result_decimal_places <= 2
    else:
        # Invalid price should raise ValidationError
        with pytest.raises(ValidationError):
            MenuItemCreate(
                name=name,
                description=description,
                price=price,
                category=category,
                stock_quantity=stock_quantity,
                stock_threshold=stock_threshold
            )


# Feature: smart-canteen-manager, Property 12: Stock Quantity Non-Negative Validation
@given(
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),
    description=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2),
    category=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    stock_quantity=st.integers(min_value=-1000, max_value=2000),
    stock_threshold=st.integers(min_value=-100, max_value=100)
)
@settings(max_examples=100)
def test_menu_item_stock_non_negative_validation(name, description, price, category, stock_quantity, stock_threshold):
    """
    Property: Menu item stock quantities and thresholds must be non-negative.
    Validates: Requirements 9.7, 17.6
    
    For any menu item:
    - stock_quantity >= 0
    - stock_threshold >= 0
    """
    assume(name.strip() and description.strip() and category.strip())
    
    is_valid_stock = stock_quantity >= 0
    is_valid_threshold = stock_threshold >= 0
    
    if is_valid_stock and is_valid_threshold:
        # Valid stock values should allow menu item creation
        menu_item = MenuItemCreate(
            name=name,
            description=description,
            price=price,
            category=category,
            stock_quantity=stock_quantity,
            stock_threshold=stock_threshold
        )
        assert menu_item.stock_quantity >= 0
        assert menu_item.stock_threshold >= 0
        assert menu_item.stock_quantity == stock_quantity
        assert menu_item.stock_threshold == stock_threshold
    else:
        # Invalid stock values should raise ValidationError
        with pytest.raises(ValidationError):
            MenuItemCreate(
                name=name,
                description=description,
                price=price,
                category=category,
                stock_quantity=stock_quantity,
                stock_threshold=stock_threshold
            )


# Feature: smart-canteen-manager, Property 13: Menu Item Update Partial Validation
@given(
    name=st.one_of(st.none(), st.text()),
    description=st.one_of(st.none(), st.text()),
    price=st.one_of(st.none(), st.decimals(min_value=Decimal("-99.99"), max_value=Decimal("99999.999"), places=None)),
    category=st.one_of(st.none(), st.text()),
    stock_quantity=st.one_of(st.none(), st.integers(min_value=-100, max_value=2000)),
    stock_threshold=st.one_of(st.none(), st.integers(min_value=-50, max_value=100)),
    is_available=st.one_of(st.none(), st.booleans())
)
@settings(max_examples=100)
def test_menu_item_update_partial_validation(name, description, price, category, stock_quantity, stock_threshold, is_available):
    """
    Property: MenuItemUpdate validates only provided fields, allows None values.
    Validates: Requirements 7.8, 17.8
    
    For any update U with optional fields F1, F2, ..., Fn:
    - If Fi is None, no validation occurs for Fi
    - If Fi is provided, normal validation rules apply to Fi
    """
    # Build update dict excluding None values for validation check
    update_fields = {}
    validation_errors = []
    
    if name is not None:
        if 1 <= len(name.strip()) <= 100 and name.strip():
            update_fields['name'] = name
        else:
            validation_errors.append('name')
    
    if description is not None:
        if 1 <= len(description.strip()) <= 500 and description.strip():
            update_fields['description'] = description
        else:
            validation_errors.append('description')
    
    if price is not None:
        decimal_places = abs(price.as_tuple().exponent) if price.as_tuple().exponent < 0 else 0
        if price >= Decimal("0.01") and price <= Decimal("9999.99") and decimal_places <= 2:
            update_fields['price'] = price
        else:
            validation_errors.append('price')
    
    if category is not None:
        if 1 <= len(category.strip()) <= 50 and category.strip():
            update_fields['category'] = category
        else:
            validation_errors.append('category')
    
    if stock_quantity is not None:
        if stock_quantity >= 0:
            update_fields['stock_quantity'] = stock_quantity
        else:
            validation_errors.append('stock_quantity')
    
    if stock_threshold is not None:
        if stock_threshold >= 0:
            update_fields['stock_threshold'] = stock_threshold
        else:
            validation_errors.append('stock_threshold')
    
    if is_available is not None:
        update_fields['is_available'] = is_available
    
    if not validation_errors:
        # All provided fields are valid - should succeed
        update = MenuItemUpdate(
            name=name,
            description=description,
            price=price,
            category=category,
            stock_quantity=stock_quantity,
            stock_threshold=stock_threshold,
            is_available=is_available
        )
        
        # Verify None fields remain None and valid fields are preserved
        if name is not None:
            assert update.name == name.strip()
        if price is not None:
            assert update.price == price
        if stock_quantity is not None:
            assert update.stock_quantity == stock_quantity
    else:
        # Some fields are invalid - should raise ValidationError
        with pytest.raises(ValidationError):
            MenuItemUpdate(
                name=name,
                description=description,
                price=price,
                category=category,
                stock_quantity=stock_quantity,
                stock_threshold=stock_threshold,
                is_available=is_available
            )