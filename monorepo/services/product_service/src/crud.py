"""CRUD operations for the Product service."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from services.product_service.src.models import Product
from shared.db.base import CRUDBase
from shared.models.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """CRUD operations for products."""
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Product]:
        """Get a product by name.
        
        Args:
            db: Database session
            name: Product name
            
        Returns:
            Product if found, None otherwise
        """
        return db.query(Product).filter(Product.name == name).first()
    
    def get_available(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get available products.
        
        Args:
            db: Database session
            skip: Number of products to skip
            limit: Maximum number of products to return
            
        Returns:
            List of available products
        """
        return (
            db.query(Product)
            .filter(Product.is_available == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """Create a new product.
        
        Args:
            db: Database session
            obj_in: Product creation data
            
        Returns:
            Created product
        """
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            stock=obj_in.stock,
            is_available=obj_in.is_available,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        """Update a product.
        
        Args:
            db: Database session
            db_obj: Product to update
            obj_in: Product update data
            
        Returns:
            Updated product
        """
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def update_stock(self, db: Session, *, product_id: UUID, quantity: int) -> Product:
        """Update product stock.
        
        Args:
            db: Database session
            product_id: Product ID
            quantity: Quantity to add (positive) or remove (negative)
            
        Returns:
            Updated product
        """
        product = self.get(db, id=product_id)
        
        if not product:
            return None
        
        product.stock += quantity
        product.updated_at = datetime.utcnow()
        
        if product.stock < 0:
            product.stock = 0
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return product


# Create a singleton instance
product = CRUDProduct(Product)
