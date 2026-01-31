"""
User Router
===========
FastAPI routes for user profile management endpoints.
All routes are prefixed with /api/users

Endpoints:
- GET  /me           - Get current user profile
- PUT  /me           - Update current user profile
- DELETE /me         - Delete current user account
- POST /me/deactivate - Deactivate current user account
- GET  /{user_id}    - Get public user profile by ID
- GET  /             - List users (with pagination)
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from controllers.user_controller import user_controller
from commons.dependencies import get_current_user
from models.user_model import User
from core.apis.schemas.requests.user_request import (
    UpdateProfileRequest,
    DeleteAccountRequest,
)
from core.apis.schemas.responses.auth_response import (
    MessageResponse,
)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


# =============================================================================
# GET CURRENT USER PROFILE
# =============================================================================


@router.get(
    "/me",
    response_model=None,
    summary="Get current user profile",
    description="Get the complete profile of the currently authenticated user.",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "phone": "+919876543210",
                            "role": "customer",
                            "profile_pic": None,
                            "is_active": True,
                            "email_verified": False,
                            "created_at": "2026-01-31T12:00:00",
                            "updated_at": "2026-01-31T12:00:00",
                        }
                    }
                }
            },
        }
    },
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.

    Returns the complete profile of the authenticated user.
    Requires valid access token in Authorization header.
    """
    return await user_controller.get_profile(user=current_user)


# =============================================================================
# UPDATE CURRENT USER PROFILE
# =============================================================================


@router.put(
    "/me",
    response_model=None,
    summary="Update current user profile",
    description="Update profile fields for the currently authenticated user.",
    responses={
        200: {
            "description": "Profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "full_name": "Jane Doe",
                            "phone": "+919876543210",
                            "role": "customer",
                            "profile_pic": "https://example.com/new-pic.jpg",
                            "is_active": True,
                            "email_verified": False,
                            "created_at": "2026-01-31T12:00:00",
                            "updated_at": "2026-01-31T12:30:00",
                        },
                        "message": "Profile updated successfully",
                    }
                }
            },
        }
    },
)
async def update_me(
    request: UpdateProfileRequest, current_user: User = Depends(get_current_user)
):
    """
    Update current user profile.

    Only provided fields will be updated. All fields are optional.

    - **full_name**: New display name
    - **phone**: New phone number
    - **profile_pic**: URL to new profile picture
    """
    return await user_controller.update_profile(
        user=current_user,
        full_name=request.full_name,
        phone=request.phone,
        profile_pic=request.profile_pic,
    )


# =============================================================================
# DELETE CURRENT USER ACCOUNT
# =============================================================================


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete current user account",
    description="Permanently delete the current user's account. Requires password confirmation.",
    responses={
        200: {
            "description": "Account deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Account deleted successfully",
                        "success": True,
                    }
                }
            },
        },
        400: {"description": "Incorrect password"},
    },
)
async def delete_me(
    request: DeleteAccountRequest, current_user: User = Depends(get_current_user)
):
    """
    Delete current user account.

    **WARNING**: This action is permanent and cannot be undone!

    Requires password confirmation to prevent accidental deletion.

    - **password**: Current account password for verification
    """
    return await user_controller.delete_account(
        user=current_user,
        password=request.password,
    )


# =============================================================================
# DEACTIVATE CURRENT USER ACCOUNT
# =============================================================================


@router.post(
    "/me/deactivate",
    response_model=MessageResponse,
    summary="Deactivate current user account",
    description="Deactivate (soft delete) the current user's account. Can be reactivated later.",
    responses={
        200: {
            "description": "Account deactivated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Account deactivated successfully",
                        "success": True,
                    }
                }
            },
        }
    },
)
async def deactivate_me(current_user: User = Depends(get_current_user)):
    """
    Deactivate current user account.

    This is a soft delete - the account can be reactivated later.
    After deactivation, the user will not be able to login.
    """
    return await user_controller.deactivate_account(user=current_user)


# =============================================================================
# GET USER BY ID (Public Profile)
# =============================================================================


@router.get(
    "/{user_id}",
    response_model=None,
    summary="Get user by ID",
    description="Get public profile of a user by their ID.",
    responses={
        200: {
            "description": "User public profile",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "full_name": "John Doe",
                            "role": "cleaner",
                            "profile_pic": "https://example.com/pic.jpg",
                            "created_at": "2026-01-31T12:00:00",
                        }
                    }
                }
            },
        },
        404: {"description": "User not found"},
    },
)
async def get_user_by_id(user_id: str):
    """
    Get user public profile.

    Returns only publicly visible information.
    Does not require authentication.

    - **user_id**: The user's unique identifier
    """
    return await user_controller.get_user_by_id(user_id=user_id)


# =============================================================================
# LIST USERS
# =============================================================================


@router.get(
    "/",
    response_model=None,
    summary="List users",
    description="Get a paginated list of users. Useful for browsing cleaners.",
    responses={
        200: {
            "description": "List of users",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {
                                "id": "507f1f77bcf86cd799439011",
                                "full_name": "John Doe",
                                "role": "cleaner",
                                "profile_pic": None,
                                "created_at": "2026-01-31T12:00:00",
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
async def list_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    role: Optional[str] = Query(
        default=None, description="Filter by role: 'customer' or 'cleaner'"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
):
    """
    List users with pagination and filtering.

    Returns public profiles only.
    Useful for customers browsing available cleaners.

    - **skip**: Pagination offset
    - **limit**: Maximum results (1-100)
    - **role**: Filter by 'customer' or 'cleaner'
    - **is_active**: Filter by active status
    """
    return await user_controller.list_users(
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )
