"""Main module for the User service."""

import os
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from services.user_service.src.crud import user
from services.user_service.src.models import User as UserModel
from shared.db.base import init_db
from shared.db.session import get_db
from shared.models.user import User, UserCreate, UserUpdate
from shared.utils.auth import create_access_token
from shared.utils.http_client import HttpClient
from shared.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Service",
    description="User service for the monorepo",
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

# Notification service URL from environment variable
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8003")

# HTTP client for notification service
notification_client = HttpClient(NOTIFICATION_SERVICE_URL)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("User service starting up")
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("User service shutting down")
    await notification_client.close()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}


@app.post("/users", response_model=User)
async def create_user(
    user_in: UserCreate, db: Session = Depends(get_db)
) -> User:
    """Create a new user.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        Created user
    """
    # Check if user with email already exists
    db_user = user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with username already exists
    db_user = user.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    db_user = user.create(db, obj_in=user_in)
    
    # Send welcome notification
    try:
        await notification_client.post(
            "notifications",
            data={
                "recipient_id": str(db_user.id),
                "type": "email",
                "subject": "Welcome to the platform",
                "content": f"Welcome {db_user.username}! Thank you for registering.",
            },
        )
    except Exception as e:
        logger.error(f"Error sending welcome notification: {e}")
    
    return db_user


@app.get("/users", response_model=List[User])
def get_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[User]:
    """Get users.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        db: Database session
        
    Returns:
        List of users
    """
    return user.get_multi(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, db: Session = Depends(get_db)) -> User:
    """Get a user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return db_user


@app.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)
) -> User:
    """Update a user.
    
    Args:
        user_id: User ID
        user_in: User update data
        db: Database session
        
    Returns:
        Updated user
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user.update(db, db_obj=db_user, obj_in=user_in)


@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> User:
    """Delete a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Deleted user
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user.remove(db, id=user_id)


@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Login a user.
    
    Args:
        email: User email
        password: User password
        db: Database session
        
    Returns:
        Access token
    """
    db_user = user.authenticate(db, email=email, password=password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active(db_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
