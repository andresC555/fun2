"""Tests for the API Gateway service."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from services.api_gateway.src.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("services.api_gateway.src.main.user_client.get")
def test_get_users(mock_get, client):
    """Test get users endpoint."""
    # Mock the response from the user service
    mock_get.return_value = AsyncMock(return_value=[{"id": "1", "username": "test"}])
    
    response = client.get("/api/users")
    assert response.status_code == 200


@patch("services.api_gateway.src.main.product_client.get")
def test_get_products(mock_get, client):
    """Test get products endpoint."""
    # Mock the response from the product service
    mock_get.return_value = AsyncMock(return_value=[{"id": "1", "name": "Test Product"}])
    
    response = client.get("/api/products")
    assert response.status_code == 200


@patch("services.api_gateway.src.main.notification_client.post")
def test_create_notification(mock_post, client):
    """Test create notification endpoint."""
    # Mock the response from the notification service
    mock_post.return_value = AsyncMock(
        return_value={"id": "1", "recipient_id": "1", "subject": "Test", "content": "Test content"}
    )
    
    response = client.post(
        "/api/notifications",
        json={"recipient_id": "1", "subject": "Test", "content": "Test content"},
    )
    assert response.status_code == 200
