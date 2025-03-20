"""Shared data models for the monorepo services."""

from shared.models.base import BaseModel
from shared.models.user import User, UserCreate, UserUpdate
from shared.models.product import Product, ProductCreate, ProductUpdate
from shared.models.notification import Notification, NotificationCreate

__all__ = [
    "BaseModel",
    "User", "UserCreate", "UserUpdate",
    "Product", "ProductCreate", "ProductUpdate",
    "Notification", "NotificationCreate",
]
