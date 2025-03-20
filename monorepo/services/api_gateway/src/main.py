"""Main module for the API Gateway service."""

import os
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.utils.http_client import HttpClient
from shared.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="API Gateway",
    description="API Gateway for the monorepo services",
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

# Service URLs from environment variables
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8003")

# HTTP clients for services
user_client = HttpClient(USER_SERVICE_URL)
product_client = HttpClient(PRODUCT_SERVICE_URL)
notification_client = HttpClient(NOTIFICATION_SERVICE_URL)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("API Gateway starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("API Gateway shutting down")
    await user_client.close()
    await product_client.close()
    await notification_client.close()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}


# User service routes
@app.get("/api/users")
async def get_users(skip: int = 0, limit: int = 100):
    """Get users.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users
    """
    try:
        return await user_client.get("users", params={"skip": skip, "limit": limit})
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Error getting users")


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get a user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User
    """
    try:
        return await user_client.get(f"users/{user_id}")
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Error getting user")


@app.post("/api/users")
async def create_user(request: Request):
    """Create a new user.
    
    Args:
        request: Request
        
    Returns:
        Created user
    """
    try:
        data = await request.json()
        return await user_client.post("users", data=data)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")


# Product service routes
@app.get("/api/products")
async def get_products(skip: int = 0, limit: int = 100):
    """Get products.
    
    Args:
        skip: Number of products to skip
        limit: Maximum number of products to return
        
    Returns:
        List of products
    """
    try:
        return await product_client.get("products", params={"skip": skip, "limit": limit})
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Error getting products")


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get a product by ID.
    
    Args:
        product_id: Product ID
        
    Returns:
        Product
    """
    try:
        return await product_client.get(f"products/{product_id}")
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(status_code=500, detail="Error getting product")


@app.post("/api/products")
async def create_product(request: Request):
    """Create a new product.
    
    Args:
        request: Request
        
    Returns:
        Created product
    """
    try:
        data = await request.json()
        return await product_client.post("products", data=data)
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Error creating product")


# Notification service routes
@app.post("/api/notifications")
async def create_notification(request: Request):
    """Create a new notification.
    
    Args:
        request: Request
        
    Returns:
        Created notification
    """
    try:
        data = await request.json()
        return await notification_client.post("notifications", data=data)
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail="Error creating notification")


@app.get("/api/notifications/{notification_id}")
async def get_notification(notification_id: str):
    """Get a notification by ID.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        Notification
    """
    try:
        return await notification_client.get(f"notifications/{notification_id}")
    except Exception as e:
        logger.error(f"Error getting notification: {e}")
        raise HTTPException(status_code=500, detail="Error getting notification")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler.
    
    Args:
        request: Request
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
