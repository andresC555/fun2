"""Tests for the Product service CRUD operations."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from services.product_service.src.crud import product
from services.product_service.src.models import Product as ProductModel
from shared.models.product import ProductCreate, ProductUpdate


def test_create_product(db: Session):
    """Test creating a product."""
    # Create a test product
    product_in = ProductCreate(
        name="Test Product",
        description="This is a test product",
        price=Decimal("19.99"),
        stock=100,
        is_available=True,
    )
    db_product = product.create(db, obj_in=product_in)
    
    # Check that the product was created correctly
    assert db_product.name == product_in.name
    assert db_product.description == product_in.description
    assert db_product.price == product_in.price
    assert db_product.stock == product_in.stock
    assert db_product.is_available == product_in.is_available


def test_get_product(db: Session):
    """Test getting a product."""
    # Create a test product
    product_in = ProductCreate(
        name="Get Product",
        description="This is a product to get",
        price=Decimal("29.99"),
        stock=50,
        is_available=True,
    )
    db_product = product.create(db, obj_in=product_in)
    
    # Test getting the product by ID
    retrieved_product = product.get(db, id=db_product.id)
    assert retrieved_product
    assert retrieved_product.id == db_product.id
    assert retrieved_product.name == db_product.name
    
    # Test getting the product by name
    retrieved_product = product.get_by_name(db, name=db_product.name)
    assert retrieved_product
    assert retrieved_product.id == db_product.id


def test_get_available_products(db: Session):
    """Test getting available products."""
    # Create available and unavailable products
    product_available = ProductCreate(
        name="Available Product",
        description="This product is available",
        price=Decimal("39.99"),
        stock=10,
        is_available=True,
    )
    product_unavailable = ProductCreate(
        name="Unavailable Product",
        description="This product is not available",
        price=Decimal("49.99"),
        stock=0,
        is_available=False,
    )
    
    db_product_available = product.create(db, obj_in=product_available)
    db_product_unavailable = product.create(db, obj_in=product_unavailable)
    
    # Test getting available products
    available_products = product.get_available(db)
    
    # Check that the available product is in the list
    assert any(p.id == db_product_available.id for p in available_products)
    
    # Check that the unavailable product is not in the list
    assert not any(p.id == db_product_unavailable.id for p in available_products)


def test_update_product(db: Session):
    """Test updating a product."""
    # Create a test product
    product_in = ProductCreate(
        name="Update Product",
        description="This product will be updated",
        price=Decimal("59.99"),
        stock=20,
        is_available=True,
    )
    db_product = product.create(db, obj_in=product_in)
    
    # Update the product
    product_update = ProductUpdate(
        name="Updated Product",
        description="This product has been updated",
        price=Decimal("69.99"),
    )
    updated_product = product.update(db, db_obj=db_product, obj_in=product_update)
    
    # Check that the product was updated correctly
    assert updated_product.id == db_product.id
    assert updated_product.name == product_update.name
    assert updated_product.description == product_update.description
    assert updated_product.price == product_update.price
    assert updated_product.stock == db_product.stock  # Unchanged
    assert updated_product.is_available == db_product.is_available  # Unchanged
    assert updated_product.updated_at is not None


def test_update_stock(db: Session):
    """Test updating product stock."""
    # Create a test product
    product_in = ProductCreate(
        name="Stock Product",
        description="This product's stock will be updated",
        price=Decimal("79.99"),
        stock=50,
        is_available=True,
    )
    db_product = product.create(db, obj_in=product_in)
    
    # Add stock
    updated_product = product.update_stock(db, product_id=db_product.id, quantity=10)
    assert updated_product.stock == 60
    
    # Remove stock
    updated_product = product.update_stock(db, product_id=db_product.id, quantity=-20)
    assert updated_product.stock == 40
    
    # Try to remove more stock than available
    updated_product = product.update_stock(db, product_id=db_product.id, quantity=-100)
    assert updated_product.stock == 0  # Stock should be set to 0, not negative


def test_delete_product(db: Session):
    """Test deleting a product."""
    # Create a test product
    product_in = ProductCreate(
        name="Delete Product",
        description="This product will be deleted",
        price=Decimal("89.99"),
        stock=30,
        is_available=True,
    )
    db_product = product.create(db, obj_in=product_in)
    
    # Delete the product
    deleted_product = product.remove(db, id=db_product.id)
    
    # Check that the product was deleted correctly
    assert deleted_product.id == db_product.id
    
    # Check that the product no longer exists
    retrieved_product = product.get(db, id=db_product.id)
    assert retrieved_product is None
