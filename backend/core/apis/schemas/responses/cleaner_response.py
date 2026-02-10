"""
Cleaner Response Schemas
========================
Pydantic models for cleaner profile-related API responses.
Includes full profiles, public profiles, and list responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LocationResponse(BaseModel):
    """Schema for location data in responses."""

    type: str = Field(default="Point", description="GeoJSON type")
    coordinates: List[float] = Field(
        ..., description="[longitude, latitude] coordinates"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "Point",
                "coordinates": [72.8777, 19.0760],
            }
        }
    }


class CleanerProfileResponse(BaseModel):
    """
    Schema for full cleaner profile response.

    Returned to the cleaner themselves (includes private fields like address).
    """

    id: str = Field(..., description="Profile unique identifier")
    user_id: str = Field(..., description="Reference to the user account")
    bio: Optional[str] = Field(None, description="Professional bio")
    experience_years: int = Field(..., description="Years of experience")
    specializations: List[str] = Field(..., description="Service specializations")

    # Location
    address: Optional[str] = Field(None, description="Full street address")
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State / province")
    pincode: Optional[str] = Field(None, description="Postal / ZIP code")
    location: Optional[LocationResponse] = Field(None, description="GeoJSON location")
    service_radius_km: float = Field(..., description="Service travel radius in km")

    # Status
    is_available: bool = Field(..., description="Currently accepting bookings")
    verified: bool = Field(..., description="Admin-verified profile")

    # Performance
    avg_rating: float = Field(..., description="Average star rating (0-5)")
    total_reviews: int = Field(..., description="Total number of reviews")
    completed_jobs: int = Field(..., description="Completed booking count")

    # Timestamps
    created_at: datetime = Field(..., description="Profile creation time")
    updated_at: datetime = Field(..., description="Last update time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "bio": "5+ years experience in deep cleaning and sanitization.",
                "experience_years": 5,
                "specializations": ["regular", "deep"],
                "address": "123 Main Street, Andheri West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400058",
                "location": {"type": "Point", "coordinates": [72.8777, 19.0760]},
                "service_radius_km": 15.0,
                "is_available": True,
                "verified": False,
                "avg_rating": 4.5,
                "total_reviews": 12,
                "completed_jobs": 25,
                "created_at": "2026-02-01T12:00:00Z",
                "updated_at": "2026-02-10T08:00:00Z",
            }
        }
    }


class CleanerPublicProfileResponse(BaseModel):
    """
    Schema for cleaner's PUBLIC profile.

    Returned when customers view a cleaner's profile.
    Excludes private info like full address and pincode.
    """

    id: str = Field(..., description="Profile unique identifier")
    user_id: str = Field(..., description="Reference to the user account")
    full_name: Optional[str] = Field(None, description="Cleaner's display name")
    profile_pic: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, description="Professional bio")
    experience_years: int = Field(..., description="Years of experience")
    specializations: List[str] = Field(..., description="Service specializations")

    # Public location (city only, not full address)
    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State / province")
    service_radius_km: float = Field(..., description="Service travel radius in km")

    # Status
    is_available: bool = Field(..., description="Currently accepting bookings")
    verified: bool = Field(..., description="Admin-verified profile")

    # Performance
    avg_rating: float = Field(..., description="Average star rating (0-5)")
    total_reviews: int = Field(..., description="Total number of reviews")
    completed_jobs: int = Field(..., description="Completed booking count")

    created_at: datetime = Field(..., description="Profile creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "full_name": "Ravi Kumar",
                "profile_pic": "https://example.com/pic.jpg",
                "bio": "Experienced home cleaner specializing in deep cleaning.",
                "experience_years": 5,
                "specializations": ["regular", "deep"],
                "city": "Mumbai",
                "state": "Maharashtra",
                "service_radius_km": 15.0,
                "is_available": True,
                "verified": True,
                "avg_rating": 4.5,
                "total_reviews": 12,
                "completed_jobs": 25,
                "created_at": "2026-02-01T12:00:00Z",
            }
        }
    }


class PaginationResponse(BaseModel):
    """Reusable pagination metadata."""

    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")
    total: int = Field(..., description="Total matching records")
    has_more: bool = Field(..., description="Whether more records exist")


class CleanerListResponse(BaseModel):
    """
    Schema for paginated list of cleaner profiles.

    Used in search results and browsing endpoints.
    """

    cleaners: List[CleanerPublicProfileResponse] = Field(
        ..., description="List of cleaner public profiles"
    )
    pagination: PaginationResponse = Field(..., description="Pagination info")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cleaners": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "user_id": "507f1f77bcf86cd799439012",
                        "full_name": "Ravi Kumar",
                        "profile_pic": None,
                        "bio": "Professional cleaner",
                        "experience_years": 5,
                        "specializations": ["regular", "deep"],
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "service_radius_km": 15.0,
                        "is_available": True,
                        "verified": True,
                        "avg_rating": 4.5,
                        "total_reviews": 12,
                        "completed_jobs": 25,
                        "created_at": "2026-02-01T12:00:00Z",
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
