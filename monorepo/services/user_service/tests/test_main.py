"""Tests for the User service API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from services.user_service.src.main import app
from services.user_service.src.models import User, Base
from shared.db.session import get_db
from shared.models.user import UserCreate


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


@patch("services.user_service.src.main.notification_client.post")
def test_create_user(mock_post, client):
    """Test create user endpoint."""
    # Mock the notification service
    mock_post.return_value = AsyncMock()
    
    # Create a test user
    response = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "hashed_password" not in data
    
    # Test creating a user with an existing email
    response = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "password123",
        },
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
    
    # Test creating a user with an existing username
    response = client.post(
        "/users",
        json={
            "email": "test2@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_get_users(client):
    """Test get users endpoint."""
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user(client):
    """Test get user endpoint."""
    # Create a test user
    response = client.post(
        "/users",
        json={
            "email": "getuser@example.com",
            "username": "getuser",
            "password": "password123",
        },
    )
    
    user_id = response.json()["id"]
    
    # Get the user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "getuser@example.com"
    assert data["username"] == "getuser"
    
    # Test getting a non-existent user
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user(client):
    """Test update user endpoint."""
    # Create a test user
    response = client.post(
        "/users",
        json={
            "email": "updateuser@example.com",
            "username": "updateuser",
            "password": "password123",
        },
    )
    
    user_id = response.json()["id"]
    
    # Update the user
    response = client.put(
        f"/users/{user_id}",
        json={
            "username": "updateduser",
            "email": "updated@example.com",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"
    
    # Test updating a non-existent user
    response = client.put(
        "/users/00000000-0000-0000-0000-000000000000",
        json={
            "username": "updateduser",
        },
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client):
    """Test delete user endpoint."""
    # Create a test user
    response = client.post(
        "/users",
        json={
            "email": "deleteuser@example.com",
            "username": "deleteuser",
            "password": "password123",
        },
    )
    
    user_id = response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    
    # Test deleting a non-existent user
    response = client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_login(client):
    """Test login endpoint."""
    # Create a test user
    response = client.post(
        "/users",
        json={
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "password123",
        },
    )
    
    # Test successful login
    response = client.post(
        "/login",
        params={
            "email": "loginuser@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Test failed login with wrong password
    response = client.post(
        "/login",
        params={
            "email": "loginuser@example.com",
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    
    # Test failed login with wrong email
    response = client.post(
        "/login",
        params={
            "email": "wrong@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
