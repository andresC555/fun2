"""Product models for the monorepo services."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from shared.models.base import BaseModel


class ProductBase(BaseModel):
    """Base product model with common fields."""
    
    name: str
    description: str
    price: Decimal
    stock: int = 0
    is_available: bool = True


class ProductCreate(BaseModel):
    """Product creation model."""
    
    name: str
    description: str
    price: Decimal
    stock: int = 0
    is_available: bool = True


class ProductUpdate(BaseModel):
    """Product update model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_available: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Product(ProductBase):
    """Complete product model."""
    
    id: UUID
