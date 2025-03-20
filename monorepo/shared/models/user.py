"""User models for the monorepo services."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from shared.models.base import BaseModel


class UserBase(BaseModel):
    """Base user model with common fields."""
    
    email: EmailStr
    username: str
    is_active: bool = True
    is_admin: bool = False


class UserCreate(BaseModel):
    """User creation model."""
    
    email: EmailStr
    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase):
    """Complete user model."""
    
    id: UUID
    hashed_password: str
