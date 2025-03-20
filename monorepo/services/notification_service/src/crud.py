"""CRUD operations for the Notification service."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from services.notification_service.src.models import Notification
from shared.db.base import CRUDBase
from shared.models.notification import NotificationCreate, NotificationStatus, NotificationType


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationCreate]):
    """CRUD operations for notifications."""
    
    def get_by_recipient(
        self, db: Session, *, recipient_id: str, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by recipient ID.
        
        Args:
            db: Database session
            recipient_id: Recipient ID
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications
        """
        return (
            db.query(Notification)
            .filter(Notification.recipient_id == recipient_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending(self, db: Session, *, limit: int = 100) -> List[Notification]:
        """Get pending notifications.
        
        Args:
            db: Database session
            limit: Maximum number of notifications to return
            
        Returns:
            List of pending notifications
        """
        return (
            db.query(Notification)
            .filter(Notification.status == NotificationStatus.PENDING)
            .order_by(Notification.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self, db: Session, *, type: NotificationType, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by type.
        
        Args:
            db: Database session
            type: Notification type
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications
        """
        return (
            db.query(Notification)
            .filter(Notification.type == type)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, db: Session, *, status: NotificationStatus, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by status.
        
        Args:
            db: Database session
            status: Notification status
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications
        """
        return (
            db.query(Notification)
            .filter(Notification.status == status)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_status(
        self, db: Session, *, notification_id: UUID, status: NotificationStatus, error_message: Optional[str] = None
    ) -> Notification:
        """Update notification status.
        
        Args:
            db: Database session
            notification_id: Notification ID
            status: New status
            error_message: Error message (for failed notifications)
            
        Returns:
            Updated notification
        """
        notification = self.get(db, id=notification_id)
        
        if not notification:
            return None
        
        notification.status = status
        notification.updated_at = datetime.utcnow()
        
        if status == NotificationStatus.SENT:
            notification.sent_at = datetime.utcnow()
        
        if error_message:
            notification.error_message = error_message
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification


# Create a singleton instance
notification = CRUDNotification(Notification)
