"""
Cleaner Router
==============
FastAPI routes for cleaner profile management endpoints.
All routes are prefixed with /api/cleaners

Endpoints:
- POST /profile       - Create cleaner profile (auth: cleaner only)
- GET  /profile/me    - Get own cleaner profile (auth: cleaner only)
- PUT  /profile/me    - Update own cleaner profile (auth: cleaner only)
- GET  /{user_id}     - Get cleaner's public profile (no auth)
- GET  /search        - Search cleaners (no auth)
- GET  /nearby        - Find nearby cleaners (no auth)
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from controllers.cleaner_controller import cleaner_controller
from commons.dependencies import get_current_user
from models.user_model import User
from core.apis.schemas.requests.cleaner_request import (
    CreateCleanerProfileRequest,
    UpdateCleanerProfileRequest,
)
from core.apis.schemas.responses.auth_response import MessageResponse

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/cleaners",
    tags=["Cleaners"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


# =============================================================================
# CREATE CLEANER PROFILE
# =============================================================================


@router.post(
    "/profile",
    status_code=status.HTTP_201_CREATED,
    summary="Create cleaner profile",
    description="Create a professional cleaner profile. Only users with role='cleaner' can create one.",
    responses={
        201: {
            "description": "Cleaner profile created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "profile": {
                            "id": "507f1f77bcf86cd799439011",
                            "user_id": "507f1f77bcf86cd799439012",
                            "bio": "Experienced cleaner",
                            "city": "Mumbai",
                            "is_available": True,
                        },
                        "message": "Cleaner profile created successfully",
                        "success": True,
                    }
                }
            },
        },
        403: {"description": "Only cleaners can create profiles"},
        409: {"description": "Profile already exists"},
    },
)
async def create_profile(
    request: CreateCleanerProfileRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a cleaner profile.

    Only users who registered with role='cleaner' can create a profile.
    Each cleaner can have only ONE profile.

    - **bio**: Professional bio (optional, max 500 chars)
    - **experience_years**: Years of experience
    - **specializations**: List of categories (regular, deep, move_in_out, office, specialized)
    - **city**: City name (required for search)
    - **latitude/longitude**: Location coordinates for nearby search
    - **service_radius_km**: How far you'll travel (1-100 km)
    """
    return await cleaner_controller.create_profile(
        user=current_user,
        bio=request.bio,
        experience_years=request.experience_years,
        specializations=request.specializations,
        address=request.address,
        city=request.city,
        state=request.state,
        pincode=request.pincode,
        latitude=request.latitude,
        longitude=request.longitude,
        service_radius_km=request.service_radius_km,
    )


# =============================================================================
# GET OWN CLEANER PROFILE
# =============================================================================


@router.get(
    "/profile/me",
    summary="Get my cleaner profile",
    description="Get the full cleaner profile for the authenticated user.",
    responses={
        200: {
            "description": "Full cleaner profile",
            "content": {
                "application/json": {
                    "example": {
                        "profile": {
                            "id": "507f1f77bcf86cd799439011",
                            "user_id": "507f1f77bcf86cd799439012",
                            "bio": "5+ years in deep cleaning",
                            "experience_years": 5,
                            "specializations": ["regular", "deep"],
                            "address": "123 Main St, Andheri",
                            "city": "Mumbai",
                            "state": "Maharashtra",
                            "pincode": "400058",
                            "service_radius_km": 15.0,
                            "is_available": True,
                            "verified": False,
                            "avg_rating": 4.5,
                            "total_reviews": 12,
                            "completed_jobs": 25,
                        }
                    }
                }
            },
        },
        403: {"description": "Only cleaners have profiles"},
        404: {"description": "Profile not found - create one first"},
    },
)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get your own cleaner profile.

    Returns the full profile including private data (address, pincode).
    Only available to users with role='cleaner'.
    """
    return await cleaner_controller.get_my_profile(user=current_user)


# =============================================================================
# UPDATE OWN CLEANER PROFILE
# =============================================================================


@router.put(
    "/profile/me",
    summary="Update my cleaner profile",
    description="Update cleaner profile fields. Only provided fields will be updated.",
    responses={
        200: {
            "description": "Profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "profile": {
                            "id": "507f1f77bcf86cd799439011",
                            "city": "Pune",
                            "is_available": True,
                        },
                        "message": "Profile updated successfully",
                        "success": True,
                    }
                }
            },
        },
        403: {"description": "Only cleaners can update profiles"},
        404: {"description": "Profile not found"},
    },
)
async def update_my_profile(
    request: UpdateCleanerProfileRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Update your cleaner profile.

    All fields are optional - only provided fields will be updated.

    - **bio**: Updated professional bio
    - **city**: New city
    - **specializations**: Updated service categories
    - **is_available**: Toggle availability
    - **latitude/longitude**: Update location coordinates
    """
    return await cleaner_controller.update_profile(
        user=current_user,
        update_data=request.model_dump(exclude_unset=True),
    )


# =============================================================================
# SEARCH CLEANERS (Public)
# =============================================================================


@router.get(
    "/search",
    summary="Search cleaners",
    description="Search for cleaners by city, specialization, rating, and more.",
    responses={
        200: {
            "description": "Search results with pagination",
            "content": {
                "application/json": {
                    "example": {
                        "cleaners": [
                            {
                                "id": "507f1f77bcf86cd799439011",
                                "full_name": "Ravi Kumar",
                                "city": "Mumbai",
                                "avg_rating": 4.5,
                                "specializations": ["regular", "deep"],
                                "is_available": True,
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
            },
        }
    },
)
async def search_cleaners(
    city: Optional[str] = Query(default=None, description="Filter by city name"),
    specialization: Optional[str] = Query(
        default=None,
        description="Filter by specialization: regular, deep, move_in_out, office, specialized",
    ),
    min_rating: Optional[float] = Query(
        default=None, ge=0.0, le=5.0, description="Minimum average rating"
    ),
    is_available: Optional[bool] = Query(
        default=None, description="Filter by availability"
    ),
    verified: Optional[bool] = Query(
        default=None, description="Filter by verified status"
    ),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=20, ge=1, le=50, description="Max results"),
    sort_by: str = Query(
        default="rating",
        description="Sort by: rating, experience, reviews, jobs",
    ),
):
    """
    Search for cleaners.

    Browse available cleaners with filtering and sorting.
    No authentication required.

    - **city**: Filter by city (exact match)
    - **specialization**: Filter by service type
    - **min_rating**: Only show cleaners rated >= this value
    - **sort_by**: Sort results by rating, experience, reviews, or jobs
    """
    return await cleaner_controller.search_cleaners(
        city=city,
        specialization=specialization,
        min_rating=min_rating,
        is_available=is_available,
        verified=verified,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
    )


# =============================================================================
# FIND NEARBY CLEANERS (Public)
# =============================================================================


@router.get(
    "/nearby",
    summary="Find nearby cleaners",
    description="Find cleaners near a given location using geospatial search.",
    responses={
        200: {
            "description": "Nearby cleaners sorted by distance",
            "content": {
                "application/json": {
                    "example": {
                        "cleaners": [
                            {
                                "id": "507f1f77bcf86cd799439011",
                                "full_name": "Ravi Kumar",
                                "city": "Mumbai",
                                "avg_rating": 4.5,
                            }
                        ],
                        "search": {
                            "latitude": 19.076,
                            "longitude": 72.8777,
                            "radius_km": 10.0,
                        },
                        "total": 1,
                    }
                }
            },
        }
    },
)
async def find_nearby(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Center latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Center longitude"),
    radius_km: float = Query(
        default=10.0, ge=1.0, le=50.0, description="Search radius in km"
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Max results"),
):
    """
    Find cleaners near a location.

    Uses MongoDB geospatial queries for distance-sorted results.
    No authentication required.

    - **latitude**: Your latitude (-90 to 90)
    - **longitude**: Your longitude (-180 to 180)
    - **radius_km**: Search radius (1-50 km)
    """
    return await cleaner_controller.find_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
    )


# =============================================================================
# GET CLEANER PUBLIC PROFILE
# =============================================================================


@router.get(
    "/{user_id}",
    summary="Get cleaner public profile",
    description="Get a cleaner's public profile by their user ID.",
    responses={
        200: {
            "description": "Cleaner's public profile",
            "content": {
                "application/json": {
                    "example": {
                        "profile": {
                            "id": "507f1f77bcf86cd799439011",
                            "user_id": "507f1f77bcf86cd799439012",
                            "full_name": "Ravi Kumar",
                            "bio": "Professional cleaner",
                            "city": "Mumbai",
                            "avg_rating": 4.5,
                            "is_available": True,
                        }
                    }
                }
            },
        },
        404: {"description": "Cleaner profile not found"},
    },
)
async def get_cleaner_profile(user_id: str):
    """
    Get a cleaner's public profile.

    Returns public information only (hides address, pincode).
    No authentication required.

    - **user_id**: The cleaner's user ID
    """
    return await cleaner_controller.get_public_profile(user_id=user_id)
