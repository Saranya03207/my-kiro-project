"""
Pydantic schemas for menu item validation.
Handles request validation and response serialization for menu items.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class MenuItemCreate(BaseModel):
    """
    Schema for creating a new menu item.
    
    Validates all required fields and enforces business rules:
    - Name: 1-100 characters
    - Description: 1-500 characters
    - Price: >= 0.01, max 2 decimal places
    - Category: 1-50 characters
    - Stock quantity: >= 0
    - Stock threshold: >= 0, defaults to 5
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    price: Decimal = Field(..., ge=0.01, le=9999.99, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=50)
    stock_quantity: int = Field(..., ge=0)
    stock_threshold: int = Field(default=5, ge=0)
    
    @field_validator('name', 'category')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty or whitespace."""
        if not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty."""
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price_decimals(cls, v: Decimal) -> Decimal:
        """Validate price has at most 2 decimal places."""
        if abs(v.as_tuple().exponent) > 2:
            raise ValueError('Price can have at most 2 decimal places')
        return v


class MenuItemUpdate(BaseModel):
    """
    Schema for updating an existing menu item.
    
    All fields are optional to support partial updates.
    When provided, validation rules from MenuItemCreate apply.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    price: Optional[Decimal] = Field(None, ge=0.01, le=9999.99, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    stock_quantity: Optional[int] = Field(None, ge=0)
    stock_threshold: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    
    @field_validator('name', 'category')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that string fields are not empty or whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v is not None else None
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip() if v is not None else None
    
    @field_validator('price')
    @classmethod
    def validate_price_decimals(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate price has at most 2 decimal places if provided."""
        if v is not None and abs(v.as_tuple().exponent) > 2:
            raise ValueError('Price can have at most 2 decimal places')
        return v


class MenuItemResponse(BaseModel):
    """
    Schema for menu item API responses.
    
    Returns all fields from the MenuItem model including
    metadata fields (id, timestamps, availability).
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
    price: Decimal
    category: str
    stock_quantity: int
    stock_threshold: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
