"""Tests for the User service CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from services.user_service.src.crud import user
from services.user_service.src.models import User as UserModel
from shared.models.user import UserCreate, UserUpdate


def test_create_user(db: Session):
    """Test creating a user."""
    # Create a test user
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    db_user = user.create(db, obj_in=user_in)
    
    # Check that the user was created correctly
    assert db_user.email == user_in.email
    assert db_user.username == user_in.username
    assert hasattr(db_user, "hashed_password")
    assert db_user.hashed_password != user_in.password


def test_authenticate_user(db: Session):
    """Test authenticating a user."""
    # Create a test user
    user_in = UserCreate(
        email="auth@example.com",
        username="authuser",
        password="password123",
    )
    db_user = user.create(db, obj_in=user_in)
    
    # Test successful authentication
    authenticated_user = user.authenticate(
        db, email=user_in.email, password=user_in.password
    )
    assert authenticated_user
    assert authenticated_user.id == db_user.id
    
    # Test failed authentication with wrong password
    authenticated_user = user.authenticate(
        db, email=user_in.email, password="wrongpassword"
    )
    assert authenticated_user is None
    
    # Test failed authentication with wrong email
    authenticated_user = user.authenticate(
        db, email="wrong@example.com", password=user_in.password
    )
    assert authenticated_user is None


def test_get_user(db: Session):
    """Test getting a user."""
    # Create a test user
    user_in = UserCreate(
        email="get@example.com",
        username="getuser",
        password="password123",
    )
    db_user = user.create(db, obj_in=user_in)
    
    # Test getting the user by ID
    retrieved_user = user.get(db, id=db_user.id)
    assert retrieved_user
    assert retrieved_user.id == db_user.id
    assert retrieved_user.email == db_user.email
    
    # Test getting the user by email
    retrieved_user = user.get_by_email(db, email=db_user.email)
    assert retrieved_user
    assert retrieved_user.id == db_user.id
    
    # Test getting the user by username
    retrieved_user = user.get_by_username(db, username=db_user.username)
    assert retrieved_user
    assert retrieved_user.id == db_user.id


def test_update_user(db: Session):
    """Test updating a user."""
    # Create a test user
    user_in = UserCreate(
        email="update@example.com",
        username="updateuser",
        password="password123",
    )
    db_user = user.create(db, obj_in=user_in)
    
    # Update the user
    user_update = UserUpdate(
        username="updateduser",
        email="updated@example.com",
    )
    updated_user = user.update(db, db_obj=db_user, obj_in=user_update)
    
    # Check that the user was updated correctly
    assert updated_user.id == db_user.id
    assert updated_user.username == user_update.username
    assert updated_user.email == user_update.email
    assert updated_user.hashed_password == db_user.hashed_password
    
    # Update the user's password
    user_update = UserUpdate(password="newpassword123")
    updated_user = user.update(db, db_obj=updated_user, obj_in=user_update)
    
    # Check that the password was updated correctly
    assert updated_user.id == db_user.id
    assert updated_user.hashed_password != db_user.hashed_password
    
    # Test authentication with the new password
    authenticated_user = user.authenticate(
        db, email=updated_user.email, password="newpassword123"
    )
    assert authenticated_user
    assert authenticated_user.id == updated_user.id


def test_delete_user(db: Session):
    """Test deleting a user."""
    # Create a test user
    user_in = UserCreate(
        email="delete@example.com",
        username="deleteuser",
        password="password123",
    )
    db_user = user.create(db, obj_in=user_in)
    
    # Delete the user
    deleted_user = user.remove(db, id=db_user.id)
    
    # Check that the user was deleted correctly
    assert deleted_user.id == db_user.id
    
    # Check that the user no longer exists
    retrieved_user = user.get(db, id=db_user.id)
    assert retrieved_user is None
