"""
Service Router
==============
FastAPI routes for service package management endpoints.
All routes are prefixed with /api/services

Endpoints:
- POST /              - Create service package (auth: cleaner only)
- GET  /me            - Get my services (auth: cleaner only)
- GET  /search        - Search services (no auth)
- GET  /cleaner/{id}  - Get cleaner's services (no auth)
- GET  /{service_id}  - Get service details (no auth)
- PUT  /{service_id}  - Update service (auth: owner only)
- DELETE /{service_id} - Delete service (auth: owner only)
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from controllers.service_controller import service_controller
from commons.dependencies import get_current_user
from models.user_model import User
from core.apis.schemas.requests.service_request import (
    CreateServiceRequest,
    UpdateServiceRequest,
)
from core.apis.schemas.responses.auth_response import MessageResponse

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/services",
    tags=["Services"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


# =============================================================================
# CREATE SERVICE PACKAGE
# =============================================================================


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create service package",
    description="Create a new cleaning service package. Only cleaners with a profile can create services.",
    responses={
        201: {
            "description": "Service created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "service": {
                            "id": "507f1f77bcf86cd799439013",
                            "cleaner_id": "507f1f77bcf86cd799439012",
                            "name": "Premium Deep Cleaning",
                            "price": 1500.0,
                            "category": "deep",
                            "price_type": "flat",
                            "duration_hours": 3.0,
                            "is_active": True,
                        },
                        "message": "Service package created successfully",
                        "success": True,
                    }
                }
            },
        },
        400: {"description": "Service limit reached (max 20)"},
        403: {"description": "Only cleaners can create services"},
        404: {"description": "Create a cleaner profile first"},
    },
)
async def create_service(
    request: CreateServiceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new service package.

    Requirements:
    1. Must be a cleaner (role='cleaner')
    2. Must have a cleaner profile already created
    3. Maximum 20 services per cleaner

    - **name**: Service display name (3-100 chars)
    - **price**: Base price amount
    - **category**: regular, deep, move_in_out, office, specialized
    - **price_type**: flat, per_hour, per_sqft
    - **duration_hours**: Estimated time (0.5-24 hours)
    """
    return await service_controller.create_service(
        user=current_user,
        name=request.name,
        price=request.price,
        description=request.description,
        category=request.category,
        price_type=request.price_type,
        duration_hours=request.duration_hours,
    )


# =============================================================================
# GET MY SERVICES (Cleaner's own services)
# =============================================================================


@router.get(
    "/me",
    summary="Get my services",
    description="Get all service packages for the current cleaner (including inactive ones).",
    responses={
        200: {
            "description": "List of cleaner's services",
            "content": {
                "application/json": {
                    "example": {
                        "services": [
                            {
                                "id": "507f1f77bcf86cd799439013",
                                "name": "Premium Deep Cleaning",
                                "price": 1500.0,
                                "category": "deep",
                                "is_active": True,
                            }
                        ],
                        "total": 1,
                    }
                }
            },
        },
        403: {"description": "Only cleaners have services"},
    },
)
async def get_my_services(current_user: User = Depends(get_current_user)):
    """
    Get all your service packages.

    Returns all services including inactive ones.
    Only available to users with role='cleaner'.
    """
    return await service_controller.get_my_services(user=current_user)


# =============================================================================
# SEARCH SERVICES (Public)
# =============================================================================


@router.get(
    "/search",
    summary="Search services",
    description="Search for cleaning services by category, price range, and more.",
    responses={
        200: {
            "description": "Search results with pagination",
            "content": {
                "application/json": {
                    "example": {
                        "services": [
                            {
                                "id": "507f1f77bcf86cd799439013",
                                "name": "Premium Deep Cleaning",
                                "price": 1500.0,
                                "category": "deep",
                                "cleaner_name": "Ravi Kumar",
                                "cleaner_rating": 4.5,
                                "cleaner_city": "Mumbai",
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
async def search_services(
    category: Optional[str] = Query(
        default=None,
        description="Filter by category: regular, deep, move_in_out, office, specialized",
    ),
    min_price: Optional[float] = Query(
        default=None, ge=0.0, description="Minimum price"
    ),
    max_price: Optional[float] = Query(
        default=None, ge=0.0, description="Maximum price"
    ),
    price_type: Optional[str] = Query(
        default=None,
        description="Filter by pricing model: flat, per_hour, per_sqft",
    ),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=20, ge=1, le=50, description="Max results"),
    sort_by: str = Query(
        default="price_low",
        description="Sort by: price_low, price_high, newest, duration",
    ),
):
    """
    Search for cleaning services.

    Browse available services with filtering and sorting.
    Results include cleaner info (name, rating, city).
    No authentication required.

    - **category**: Filter by cleaning type
    - **min_price / max_price**: Price range filter
    - **price_type**: Filter by pricing model
    - **sort_by**: Sort results
    """
    return await service_controller.search_services(
        category=category,
        min_price=min_price,
        max_price=max_price,
        price_type=price_type,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
    )


# =============================================================================
# GET SERVICES BY CLEANER (Public)
# =============================================================================


@router.get(
    "/cleaner/{user_id}",
    summary="Get cleaner's services",
    description="Get all active services offered by a specific cleaner.",
    responses={
        200: {
            "description": "List of cleaner's active services",
            "content": {
                "application/json": {
                    "example": {
                        "services": [
                            {
                                "id": "507f1f77bcf86cd799439013",
                                "name": "Premium Deep Cleaning",
                                "price": 1500.0,
                                "category": "deep",
                                "is_active": True,
                            }
                        ],
                        "total": 1,
                    }
                }
            },
        }
    },
)
async def get_cleaner_services(user_id: str):
    """
    Get services offered by a specific cleaner.

    Returns only active services (for customer browsing).
    No authentication required.

    - **user_id**: The cleaner's user ID
    """
    return await service_controller.get_services_by_cleaner(user_id=user_id)


# =============================================================================
# GET SERVICE BY ID
# =============================================================================


@router.get(
    "/{service_id}",
    summary="Get service details",
    description="Get full details of a specific service package.",
    responses={
        200: {
            "description": "Service package details",
            "content": {
                "application/json": {
                    "example": {
                        "service": {
                            "id": "507f1f77bcf86cd799439013",
                            "cleaner_id": "507f1f77bcf86cd799439012",
                            "name": "Premium Deep Cleaning",
                            "description": "Complete deep cleaning of entire home.",
                            "category": "deep",
                            "price": 1500.0,
                            "price_type": "flat",
                            "duration_hours": 3.0,
                            "is_active": True,
                        }
                    }
                }
            },
        },
        404: {"description": "Service not found"},
    },
)
async def get_service(service_id: str):
    """
    Get service package details.

    Returns full details of a service package.
    No authentication required.

    - **service_id**: The service's unique identifier
    """
    return await service_controller.get_service(service_id=service_id)


# =============================================================================
# UPDATE SERVICE
# =============================================================================


@router.put(
    "/{service_id}",
    summary="Update service package",
    description="Update a service package. Only the owning cleaner can update.",
    responses={
        200: {
            "description": "Service updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "service": {
                            "id": "507f1f77bcf86cd799439013",
                            "name": "Updated Service Name",
                            "price": 2000.0,
                        },
                        "message": "Service updated successfully",
                        "success": True,
                    }
                }
            },
        },
        403: {"description": "You can only update your own services"},
        404: {"description": "Service not found"},
    },
)
async def update_service(
    service_id: str,
    request: UpdateServiceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Update a service package.

    Only the cleaner who created the service can update it.
    All fields are optional - only provided fields will be updated.

    - **name**: Updated display name
    - **price**: Updated price
    - **category**: Updated category
    - **is_active**: Activate or deactivate
    """
    return await service_controller.update_service(
        user=current_user,
        service_id=service_id,
        update_data=request.model_dump(exclude_unset=True),
    )


# =============================================================================
# DELETE SERVICE
# =============================================================================


@router.delete(
    "/{service_id}",
    response_model=MessageResponse,
    summary="Delete service package",
    description="Permanently delete a service package. Only the owning cleaner can delete.",
    responses={
        200: {
            "description": "Service deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Service deleted successfully",
                        "success": True,
                    }
                }
            },
        },
        403: {"description": "You can only delete your own services"},
        404: {"description": "Service not found"},
    },
)
async def delete_service(
    service_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a service package.

    **WARNING**: This action is permanent!

    Only the cleaner who created the service can delete it.

    - **service_id**: The service's unique identifier
    """
    return await service_controller.delete_service(
        user=current_user,
        service_id=service_id,
    )
