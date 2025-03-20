"""Main module for the Notification service."""

from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from services.notification_service.src.crud import notification
from services.notification_service.src.models import Notification as NotificationModel
from services.notification_service.src.worker import celery_app, send_notification
from shared.db.base import init_db
from shared.db.session import get_db
from shared.models.notification import Notification, NotificationCreate, NotificationStatus, NotificationType
from shared.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Notification service for the monorepo",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Notification service starting up")
    init_db()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}


@app.post("/notifications", response_model=Notification)
async def create_notification(
    notification_in: NotificationCreate, db: Session = Depends(get_db)
) -> Notification:
    """Create a new notification.
    
    Args:
        notification_in: Notification creation data
        db: Database session
        
    Returns:
        Created notification
    """
    # Create notification
    db_notification = notification.create(db, obj_in=notification_in)
    
    # Queue notification for sending
    send_notification.delay(str(db_notification.id))
    
    return db_notification


@app.get("/notifications", response_model=List[Notification])
def get_notifications(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Notification]:
    """Get notifications.
    
    Args:
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        db: Database session
        
    Returns:
        List of notifications
    """
    return notification.get_multi(db, skip=skip, limit=limit)


@app.get("/notifications/{notification_id}", response_model=Notification)
def get_notification(notification_id: str, db: Session = Depends(get_db)) -> Notification:
    """Get a notification by ID.
    
    Args:
        notification_id: Notification ID
        db: Database session
        
    Returns:
        Notification
    """
    db_notification = notification.get(db, id=notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return db_notification


@app.get("/notifications/recipient/{recipient_id}", response_model=List[Notification])
def get_notifications_by_recipient(
    recipient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Notification]:
    """Get notifications by recipient ID.
    
    Args:
        recipient_id: Recipient ID
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        db: Database session
        
    Returns:
        List of notifications
    """
    return notification.get_by_recipient(db, recipient_id=recipient_id, skip=skip, limit=limit)


@app.get("/notifications/type/{notification_type}", response_model=List[Notification])
def get_notifications_by_type(
    notification_type: NotificationType, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Notification]:
    """Get notifications by type.
    
    Args:
        notification_type: Notification type
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        db: Database session
        
    Returns:
        List of notifications
    """
    return notification.get_by_type(db, type=notification_type, skip=skip, limit=limit)


@app.get("/notifications/status/{notification_status}", response_model=List[Notification])
def get_notifications_by_status(
    notification_status: NotificationStatus, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Notification]:
    """Get notifications by status.
    
    Args:
        notification_status: Notification status
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        db: Database session
        
    Returns:
        List of notifications
    """
    return notification.get_by_status(db, status=notification_status, skip=skip, limit=limit)


@app.post("/notifications/{notification_id}/resend", response_model=Notification)
def resend_notification(notification_id: str, db: Session = Depends(get_db)) -> Notification:
    """Resend a notification.
    
    Args:
        notification_id: Notification ID
        db: Database session
        
    Returns:
        Updated notification
    """
    db_notification = notification.get(db, id=notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    # Update notification status to pending
    db_notification = notification.update_status(
        db, notification_id=db_notification.id, status=NotificationStatus.PENDING
    )
    
    # Queue notification for sending
    send_notification.delay(str(db_notification.id))
    
    return db_notification


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
