"""Tests for the Notification service API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from services.notification_service.src.main import app
from services.notification_service.src.models import Notification, Base
from shared.db.session import get_db
from shared.models.notification import NotificationCreate, NotificationStatus, NotificationType


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


@patch("services.notification_service.src.main.send_notification.delay")
def test_create_notification(mock_delay, client):
    """Test create notification endpoint."""
    # Create a test notification
    response = client.post(
        "/notifications",
        json={
            "recipient_id": "test-recipient",
            "type": "email",
            "subject": "Test Subject",
            "content": "This is a test notification",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["recipient_id"] == "test-recipient"
    assert data["type"] == "email"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "This is a test notification"
    assert data["status"] == "pending"
    assert "id" in data
    
    # Check that the task was queued
    mock_delay.assert_called_once_with(data["id"])


def test_get_notifications(client):
    """Test get notifications endpoint."""
    response = client.get("/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notification(client):
    """Test get notification endpoint."""
    # Create a test notification
    response = client.post(
        "/notifications",
        json={
            "recipient_id": "get-recipient",
            "type": "email",
            "subject": "Get Subject",
            "content": "This is a notification to get",
        },
    )
    
    notification_id = response.json()["id"]
    
    # Get the notification
    response = client.get(f"/notifications/{notification_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id
    assert data["recipient_id"] == "get-recipient"
    assert data["subject"] == "Get Subject"
    
    # Test getting a non-existent notification
    response = client.get("/notifications/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_get_notifications_by_recipient(client):
    """Test get notifications by recipient endpoint."""
    # Create test notifications for the same recipient
    recipient_id = "recipient-test"
    
    client.post(
        "/notifications",
        json={
            "recipient_id": recipient_id,
            "type": "email",
            "subject": "Subject 1",
            "content": "Content 1",
        },
    )
    
    client.post(
        "/notifications",
        json={
            "recipient_id": recipient_id,
            "type": "sms",
            "subject": "Subject 2",
            "content": "Content 2",
        },
    )
    
    # Get notifications by recipient
    response = client.get(f"/notifications/recipient/{recipient_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert all(notification["recipient_id"] == recipient_id for notification in data)


def test_get_notifications_by_type(client):
    """Test get notifications by type endpoint."""
    # Create test notifications with different types
    client.post(
        "/notifications",
        json={
            "recipient_id": "type-test-1",
            "type": "email",
            "subject": "Email Subject",
            "content": "Email Content",
        },
    )
    
    client.post(
        "/notifications",
        json={
            "recipient_id": "type-test-2",
            "type": "sms",
            "subject": "SMS Subject",
            "content": "SMS Content",
        },
    )
    
    # Get notifications by type
    response = client.get("/notifications/type/email")
    assert response.status_code == 200
    email_data = response.json()
    assert isinstance(email_data, list)
    assert all(notification["type"] == "email" for notification in email_data)
    
    response = client.get("/notifications/type/sms")
    assert response.status_code == 200
    sms_data = response.json()
    assert isinstance(sms_data, list)
    assert all(notification["type"] == "sms" for notification in sms_data)


def test_get_notifications_by_status(client):
    """Test get notifications by status endpoint."""
    # Create a test notification (will be pending by default)
    response = client.post(
        "/notifications",
        json={
            "recipient_id": "status-test",
            "type": "email",
            "subject": "Status Subject",
            "content": "Status Content",
        },
    )
    
    # Get notifications by status
    response = client.get("/notifications/status/pending")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(notification["status"] == "pending" for notification in data)


@patch("services.notification_service.src.main.send_notification.delay")
def test_resend_notification(mock_delay, client):
    """Test resend notification endpoint."""
    # Create a test notification
    response = client.post(
        "/notifications",
        json={
            "recipient_id": "resend-test",
            "type": "email",
            "subject": "Resend Subject",
            "content": "Resend Content",
        },
    )
    
    notification_id = response.json()["id"]
    
    # Reset the mock to clear the first call
    mock_delay.reset_mock()
    
    # Resend the notification
    response = client.post(f"/notifications/{notification_id}/resend")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id
    assert data["status"] == "pending"
    
    # Check that the task was queued
    mock_delay.assert_called_once_with(notification_id)
    
    # Test resending a non-existent notification
    response = client.post("/notifications/00000000-0000-0000-0000-000000000000/resend")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"
