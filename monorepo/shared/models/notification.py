"""Notification models for the monorepo services."""

from enum import Enum
from typing import Optional
from uuid import UUID

from shared.models.base import BaseModel


class NotificationType(str, Enum):
    """Notification types."""
    
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification status."""
    
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationBase(BaseModel):
    """Base notification model with common fields."""
    
    recipient_id: UUID
    type: NotificationType
    subject: str
    content: str
    status: NotificationStatus = NotificationStatus.PENDING


class NotificationCreate(BaseModel):
    """Notification creation model."""
    
    recipient_id: UUID
    type: NotificationType
    subject: str
    content: str


class Notification(NotificationBase):
    """Complete notification model."""
    
    id: UUID
    error_message: Optional[str] = None
