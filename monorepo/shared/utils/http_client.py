"""HTTP client for service-to-service communication."""

import json
from typing import Any, Dict, Optional, Union

import httpx
from pydantic import BaseModel


class HttpClient:
    """HTTP client for service-to-service communication."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """Initialize the HTTP client.
        
        Args:
            base_url: Base URL for the service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send a GET request.
        
        Args:
            path: Request path
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def post(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a POST request.
        
        Args:
            path: Request path
            data: Request data
            headers: Request headers
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        if isinstance(data, BaseModel):
            data = json.loads(data.json())
        
        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def put(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a PUT request.
        
        Args:
            path: Request path
            data: Request data
            headers: Request headers
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        if isinstance(data, BaseModel):
            data = json.loads(data.json())
        
        response = await self.client.put(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def delete(
        self, path: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send a DELETE request.
        
        Args:
            path: Request path
            headers: Request headers
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
