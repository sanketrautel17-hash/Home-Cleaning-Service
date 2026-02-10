"""
Service Response Schemas
========================
Pydantic models for service package-related API responses.
Includes individual service details and list responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from core.apis.schemas.responses.cleaner_response import PaginationResponse


class ServiceResponse(BaseModel):
    """
    Schema for a single service package response.

    Returned when viewing, creating, or updating a service.
    """

    id: str = Field(..., description="Service unique identifier")
    cleaner_id: str = Field(..., description="ID of the cleaner who offers this")
    name: str = Field(..., description="Service display name")
    description: Optional[str] = Field(None, description="Service description")
    category: str = Field(..., description="Service category")
    price: float = Field(..., description="Base price amount")
    price_type: str = Field(..., description="Pricing model (flat/per_hour/per_sqft)")
    duration_hours: float = Field(..., description="Estimated duration in hours")
    is_active: bool = Field(..., description="Whether service is currently offered")
    created_at: datetime = Field(..., description="Service creation time")
    updated_at: datetime = Field(..., description="Last update time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "cleaner_id": "507f1f77bcf86cd799439012",
                "name": "Premium Deep Cleaning",
                "description": "Complete deep cleaning including kitchen, bathrooms, and all rooms.",
                "category": "deep",
                "price": 1500.0,
                "price_type": "flat",
                "duration_hours": 3.0,
                "is_active": True,
                "created_at": "2026-02-01T12:00:00Z",
                "updated_at": "2026-02-10T08:00:00Z",
            }
        }
    }


class ServiceWithCleanerResponse(BaseModel):
    """
    Schema for a service with basic cleaner info attached.

    Used in search results so customers can see who offers the service.
    """

    id: str = Field(..., description="Service unique identifier")
    cleaner_id: str = Field(..., description="ID of the cleaner")
    cleaner_name: Optional[str] = Field(None, description="Cleaner's display name")
    cleaner_rating: float = Field(default=0.0, description="Cleaner's average rating")
    cleaner_city: Optional[str] = Field(None, description="Cleaner's city")
    name: str = Field(..., description="Service display name")
    description: Optional[str] = Field(None, description="Service description")
    category: str = Field(..., description="Service category")
    price: float = Field(..., description="Base price amount")
    price_type: str = Field(..., description="Pricing model")
    duration_hours: float = Field(..., description="Estimated duration in hours")
    is_active: bool = Field(..., description="Whether service is currently offered")
    created_at: datetime = Field(..., description="Service creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "cleaner_id": "507f1f77bcf86cd799439012",
                "cleaner_name": "Ravi Kumar",
                "cleaner_rating": 4.5,
                "cleaner_city": "Mumbai",
                "name": "Premium Deep Cleaning",
                "description": "Complete deep cleaning of entire home.",
                "category": "deep",
                "price": 1500.0,
                "price_type": "flat",
                "duration_hours": 3.0,
                "is_active": True,
                "created_at": "2026-02-01T12:00:00Z",
            }
        }
    }


class ServiceListResponse(BaseModel):
    """
    Schema for paginated list of services.

    Used in search results and cleaner service listings.
    """

    services: List[ServiceResponse] = Field(..., description="List of service packages")
    pagination: PaginationResponse = Field(..., description="Pagination info")

    model_config = {
        "json_schema_extra": {
            "example": {
                "services": [
                    {
                        "id": "507f1f77bcf86cd799439013",
                        "cleaner_id": "507f1f77bcf86cd799439012",
                        "name": "Premium Deep Cleaning",
                        "description": "Complete deep cleaning of entire home.",
                        "category": "deep",
                        "price": 1500.0,
                        "price_type": "flat",
                        "duration_hours": 3.0,
                        "is_active": True,
                        "created_at": "2026-02-01T12:00:00Z",
                        "updated_at": "2026-02-10T08:00:00Z",
                    }
                ],
                "pagination": {
                    "skip": 0,
                    "limit": 20,
                    "total": 1,
                    "has_more": False,
                },
            }
        }
    }
