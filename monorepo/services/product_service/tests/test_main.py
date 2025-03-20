"""Tests for the Product service API endpoints."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from services.product_service.src.main import app
from services.product_service.src.models import Product, Base
from shared.db.session import get_db
from shared.models.product import ProductCreate


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create the database tables
Base.metadata.create_all(bind=engine)


# Override the get_db dependency
def override_get_db():
    """Override the get_db dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("services.product_service.src.main.notification_client.post")
def test_create_product(mock_post, client):
    """Test create product endpoint."""
    # Mock the notification service
    mock_post.return_value = AsyncMock()
    
    # Create a test product
    response = client.post(
        "/products",
        json={
            "name": "Test Product",
            "description": "This is a test product",
            "price": "19.99",
            "stock": 100,
            "is_available": True,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["description"] == "This is a test product"
    assert data["price"] == "19.99"
    assert data["stock"] == 100
    assert data["is_available"] is True
    assert "id" in data
    
    # Test creating a product with an existing name
    response = client.post(
        "/products",
        json={
            "name": "Test Product",
            "description": "This is another test product",
            "price": "29.99",
            "stock": 50,
            "is_available": True,
        },
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Product with this name already exists"


def test_get_products(client):
    """Test get products endpoint."""
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_available_products(client):
    """Test get available products endpoint."""
    # Create an available product
    client.post(
        "/products",
        json={
            "name": "Available Product",
            "description": "This product is available",
            "price": "39.99",
            "stock": 10,
            "is_available": True,
        },
    )
    
    # Create an unavailable product
    client.post(
        "/products",
        json={
            "name": "Unavailable Product",
            "description": "This product is not available",
            "price": "49.99",
            "stock": 0,
            "is_available": False,
        },
    )
    
    # Get available products
    response = client.get("/products/available")
    assert response.status_code == 200
    data = response.json()
    
    # Check that the available product is in the list
    assert any(p["name"] == "Available Product" for p in data)
    
    # Check that the unavailable product is not in the list
    assert not any(p["name"] == "Unavailable Product" for p in data)


def test_get_product(client):
    """Test get product endpoint."""
    # Create a test product
    response = client.post(
        "/products",
        json={
            "name": "Get Product",
            "description": "This is a product to get",
            "price": "59.99",
            "stock": 20,
            "is_available": True,
        },
    )
    
    product_id = response.json()["id"]
    
    # Get the product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Get Product"
    assert data["description"] == "This is a product to get"
    
    # Test getting a non-existent product
    response = client.get("/products/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client):
    """Test update product endpoint."""
    # Create a test product
    response = client.post(
        "/products",
        json={
            "name": "Update Product",
            "description": "This product will be updated",
            "price": "69.99",
            "stock": 30,
            "is_available": True,
        },
    )
    
    product_id = response.json()["id"]
    
    # Update the product
    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "This product has been updated",
            "price": "79.99",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Updated Product"
    assert data["description"] == "This product has been updated"
    assert data["price"] == "79.99"
    
    # Test updating a non-existent product
    response = client.put(
        "/products/00000000-0000-0000-0000-000000000000",
        json={
            "name": "Non-existent Product",
        },
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_stock(client):
    """Test update product stock endpoint."""
    # Create a test product
    response = client.post(
        "/products",
        json={
            "name": "Stock Product",
            "description": "This product's stock will be updated",
            "price": "89.99",
            "stock": 40,
            "is_available": True,
        },
    )
    
    product_id = response.json()["id"]
    
    # Add stock
    response = client.put(f"/products/{product_id}/stock?quantity=10")
    assert response.status_code == 200
    data = response.json()
    assert data["stock"] == 50
    
    # Remove stock
    response = client.put(f"/products/{product_id}/stock?quantity=-20")
    assert response.status_code == 200
    data = response.json()
    assert data["stock"] == 30
    
    # Test updating stock for a non-existent product
    response = client.put("/products/00000000-0000-0000-0000-000000000000/stock?quantity=10")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product(client):
    """Test delete product endpoint."""
    # Create a test product
    response = client.post(
        "/products",
        json={
            "name": "Delete Product",
            "description": "This product will be deleted",
            "price": "99.99",
            "stock": 50,
            "is_available": True,
        },
    )
    
    product_id = response.json()["id"]
    
    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    
    # Test deleting a non-existent product
    response = client.delete("/products/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
