"""Tests for the Notification service CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from services.notification_service.src.crud import notification
from services.notification_service.src.models import Notification as NotificationModel
from shared.models.notification import NotificationCreate, NotificationStatus, NotificationType


def test_create_notification(db: Session):
    """Test creating a notification."""
    # Create a test notification
    notification_in = NotificationCreate(
        recipient_id="test-recipient",
        type=NotificationType.EMAIL,
        subject="Test Subject",
        content="This is a test notification",
    )
    db_notification = notification.create(db, obj_in=notification_in)
    
    # Check that the notification was created correctly
    assert db_notification.recipient_id == notification_in.recipient_id
    assert db_notification.type == notification_in.type
    assert db_notification.subject == notification_in.subject
    assert db_notification.content == notification_in.content
    assert db_notification.status == NotificationStatus.PENDING


def test_get_notification(db: Session):
    """Test getting a notification."""
    # Create a test notification
    notification_in = NotificationCreate(
        recipient_id="get-recipient",
        type=NotificationType.EMAIL,
        subject="Get Subject",
        content="This is a notification to get",
    )
    db_notification = notification.create(db, obj_in=notification_in)
    
    # Test getting the notification by ID
    retrieved_notification = notification.get(db, id=db_notification.id)
    assert retrieved_notification
    assert retrieved_notification.id == db_notification.id
    assert retrieved_notification.recipient_id == db_notification.recipient_id


def test_get_by_recipient(db: Session):
    """Test getting notifications by recipient."""
    # Create test notifications for the same recipient
    recipient_id = "recipient-test"
    
    notification_in1 = NotificationCreate(
        recipient_id=recipient_id,
        type=NotificationType.EMAIL,
        subject="Subject 1",
        content="Content 1",
    )
    notification_in2 = NotificationCreate(
        recipient_id=recipient_id,
        type=NotificationType.SMS,
        subject="Subject 2",
        content="Content 2",
    )
    
    db_notification1 = notification.create(db, obj_in=notification_in1)
    db_notification2 = notification.create(db, obj_in=notification_in2)
    
    # Test getting notifications by recipient
    recipient_notifications = notification.get_by_recipient(db, recipient_id=recipient_id)
    
    assert len(recipient_notifications) >= 2
    assert any(n.id == db_notification1.id for n in recipient_notifications)
    assert any(n.id == db_notification2.id for n in recipient_notifications)


def test_get_by_type(db: Session):
    """Test getting notifications by type."""
    # Create test notifications with different types
    notification_in_email = NotificationCreate(
        recipient_id="type-test-1",
        type=NotificationType.EMAIL,
        subject="Email Subject",
        content="Email Content",
    )
    notification_in_sms = NotificationCreate(
        recipient_id="type-test-2",
        type=NotificationType.SMS,
        subject="SMS Subject",
        content="SMS Content",
    )
    
    db_notification_email = notification.create(db, obj_in=notification_in_email)
    db_notification_sms = notification.create(db, obj_in=notification_in_sms)
    
    # Test getting notifications by type
    email_notifications = notification.get_by_type(db, type=NotificationType.EMAIL)
    sms_notifications = notification.get_by_type(db, type=NotificationType.SMS)
    
    assert any(n.id == db_notification_email.id for n in email_notifications)
    assert any(n.id == db_notification_sms.id for n in sms_notifications)


def test_get_by_status(db: Session):
    """Test getting notifications by status."""
    # Create a test notification
    notification_in = NotificationCreate(
        recipient_id="status-test",
        type=NotificationType.EMAIL,
        subject="Status Subject",
        content="Status Content",
    )
    db_notification = notification.create(db, obj_in=notification_in)
    
    # Test getting notifications by status
    pending_notifications = notification.get_by_status(db, status=NotificationStatus.PENDING)
    
    assert any(n.id == db_notification.id for n in pending_notifications)
    
    # Update notification status
    updated_notification = notification.update_status(
        db, notification_id=db_notification.id, status=NotificationStatus.SENT
    )
    
    # Test getting notifications by the new status
    sent_notifications = notification.get_by_status(db, status=NotificationStatus.SENT)
    
    assert any(n.id == db_notification.id for n in sent_notifications)


def test_update_status(db: Session):
    """Test updating notification status."""
    # Create a test notification
    notification_in = NotificationCreate(
        recipient_id="update-test",
        type=NotificationType.EMAIL,
        subject="Update Subject",
        content="Update Content",
    )
    db_notification = notification.create(db, obj_in=notification_in)
    
    # Test initial status
    assert db_notification.status == NotificationStatus.PENDING
    
    # Update to processing
    updated_notification = notification.update_status(
        db, notification_id=db_notification.id, status=NotificationStatus.PROCESSING
    )
    assert updated_notification.status == NotificationStatus.PROCESSING
    
    # Update to sent
    updated_notification = notification.update_status(
        db, notification_id=db_notification.id, status=NotificationStatus.SENT
    )
    assert updated_notification.status == NotificationStatus.SENT
    assert updated_notification.sent_at is not None
    
    # Update to failed with error message
    error_message = "Test error message"
    updated_notification = notification.update_status(
        db,
        notification_id=db_notification.id,
        status=NotificationStatus.FAILED,
        error_message=error_message,
    )
    assert updated_notification.status == NotificationStatus.FAILED
    assert updated_notification.error_message == error_message
