"""Main module for the Product service."""

import os
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from services.product_service.src.crud import product
from services.product_service.src.models import Product as ProductModel
from shared.db.base import init_db
from shared.db.session import get_db
from shared.models.product import Product, ProductCreate, ProductUpdate
from shared.utils.http_client import HttpClient
from shared.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Product Service",
    description="Product service for the monorepo",
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
    logger.info("Product service starting up")
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Product service shutting down")
    await notification_client.close()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}


@app.post("/products", response_model=Product)
async def create_product(
    product_in: ProductCreate, db: Session = Depends(get_db)
) -> Product:
    """Create a new product.
    
    Args:
        product_in: Product creation data
        db: Database session
        
    Returns:
        Created product
    """
    # Check if product with name already exists
    db_product = product.get_by_name(db, name=product_in.name)
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists",
        )
    
    # Create product
    db_product = product.create(db, obj_in=product_in)
    
    # Send notification about new product
    try:
        await notification_client.post(
            "notifications",
            data={
                "recipient_id": "admin",  # In a real app, this would be a real user ID
                "type": "email",
                "subject": "New product added",
                "content": f"New product added: {db_product.name}",
            },
        )
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
    
    return db_product


@app.get("/products", response_model=List[Product])
def get_products(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Product]:
    """Get products.
    
    Args:
        skip: Number of products to skip
        limit: Maximum number of products to return
        db: Database session
        
    Returns:
        List of products
    """
    return product.get_multi(db, skip=skip, limit=limit)


@app.get("/products/available", response_model=List[Product])
def get_available_products(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Product]:
    """Get available products.
    
    Args:
        skip: Number of products to skip
        limit: Maximum number of products to return
        db: Database session
        
    Returns:
        List of available products
    """
    return product.get_available(db, skip=skip, limit=limit)


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str, db: Session = Depends(get_db)) -> Product:
    """Get a product by ID.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Product
    """
    db_product = product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return db_product


@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: str, product_in: ProductUpdate, db: Session = Depends(get_db)
) -> Product:
    """Update a product.
    
    Args:
        product_id: Product ID
        product_in: Product update data
        db: Database session
        
    Returns:
        Updated product
    """
    db_product = product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product.update(db, db_obj=db_product, obj_in=product_in)


@app.put("/products/{product_id}/stock", response_model=Product)
def update_product_stock(
    product_id: str, quantity: int, db: Session = Depends(get_db)
) -> Product:
    """Update product stock.
    
    Args:
        product_id: Product ID
        quantity: Quantity to add (positive) or remove (negative)
        db: Database session
        
    Returns:
        Updated product
    """
    db_product = product.update_stock(db, product_id=product_id, quantity=quantity)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Send notification if stock is low
    if db_product.stock < 10:
        try:
            notification_client.post(
                "notifications",
                data={
                    "recipient_id": "admin",  # In a real app, this would be a real user ID
                    "type": "email",
                    "subject": "Low stock alert",
                    "content": f"Product {db_product.name} is low on stock: {db_product.stock} remaining",
                },
            )
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    return db_product


@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: str, db: Session = Depends(get_db)) -> Product:
    """Delete a product.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Deleted product
    """
    db_product = product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product.remove(db, id=product_id)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
