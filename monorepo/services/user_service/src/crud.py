"""CRUD operations for the User service."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from services.user_service.src.models import User
from shared.db.base import CRUDBase
from shared.models.user import UserCreate, UserUpdate
from shared.utils.auth import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for users."""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user.
        
        Args:
            db: Database session
            obj_in: User creation data
            
        Returns:
            Created user
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_admin=obj_in.is_admin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update a user.
        
        Args:
            db: Database session
            db_obj: User to update
            obj_in: User update data
            
        Returns:
            Updated user
        """
        update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        update_data["updated_at"] = datetime.utcnow()
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.get_by_email(db, email=email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if a user is active.
        
        Args:
            user: User
            
        Returns:
            True if user is active, False otherwise
        """
        return user.is_active
    
    def is_admin(self, user: User) -> bool:
        """Check if a user is an admin.
        
        Args:
            user: User
            
        Returns:
            True if user is an admin, False otherwise
        """
        return user.is_admin


# Create a singleton instance
user = CRUDUser(User)
