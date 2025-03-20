"""Celery worker for the Notification service."""

import os
from typing import Dict, Optional

from celery import Celery

from services.notification_service.src.crud import notification
from services.notification_service.src.sender import NotificationSender
from shared.db.session import SessionLocal
from shared.models.notification import NotificationStatus
from shared.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery("notification_service", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)


@celery_app.task(name="send_notification")
def send_notification(notification_id: str) -> Dict[str, str]:
    """Send a notification.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        Result of the operation
    """
    logger.info(f"Processing notification {notification_id}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get notification from database
        db_notification = notification.get(db, id=notification_id)
        
        if not db_notification:
            logger.error(f"Notification {notification_id} not found")
            return {"status": "failed", "message": "Notification not found"}
        
        # Check if notification is already processed
        if db_notification.status != NotificationStatus.PENDING:
            logger.warning(f"Notification {notification_id} already processed")
            return {
                "status": "skipped",
                "message": f"Notification already processed with status {db_notification.status}",
            }
        
        # Update notification status to processing
        notification.update_status(
            db, notification_id=db_notification.id, status=NotificationStatus.PROCESSING
        )
        
        # Since we can't use await in a non-async function, we'll use the synchronous version
        # In a real application, you would use a proper async solution or run in an event loop
        import asyncio
        
        # Create an event loop and run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            NotificationSender.send(
                db_notification.type,
                db_notification.recipient_id,
                db_notification.subject,
                db_notification.content,
            )
        )
        loop.close()
        
        # Update notification status based on result
        if result["status"] == "sent":
            notification.update_status(
                db, notification_id=db_notification.id, status=NotificationStatus.SENT
            )
            logger.info(f"Notification {notification_id} sent successfully")
        else:
            notification.update_status(
                db,
                notification_id=db_notification.id,
                status=NotificationStatus.FAILED,
                error_message=result["message"],
            )
            logger.error(f"Failed to send notification {notification_id}: {result['message']}")
        
        return result
    
    except Exception as e:
        logger.exception(f"Error processing notification {notification_id}: {e}")
        
        # Update notification status to failed
        notification.update_status(
            db,
            notification_id=notification_id,
            status=NotificationStatus.FAILED,
            error_message=str(e),
        )
        
        return {"status": "failed", "message": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="process_pending_notifications")
def process_pending_notifications(limit: int = 100) -> Dict[str, int]:
    """Process pending notifications.
    
    Args:
        limit: Maximum number of notifications to process
        
    Returns:
        Result of the operation
    """
    logger.info(f"Processing up to {limit} pending notifications")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get pending notifications
        pending_notifications = notification.get_pending(db, limit=limit)
        
        # Process each notification
        for db_notification in pending_notifications:
            send_notification.delay(str(db_notification.id))
        
        return {"status": "success", "count": len(pending_notifications)}
    
    except Exception as e:
        logger.exception(f"Error processing pending notifications: {e}")
        return {"status": "failed", "message": str(e)}
    
    finally:
        db.close()


# Schedule periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks."""
    # Process pending notifications every minute
    sender.add_periodic_task(60.0, process_pending_notifications.s(100), name="process_pending_notifications")
