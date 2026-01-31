"""
Auth Response Schemas
=====================
Pydantic models for authentication-related API responses.
Includes token responses, user profiles, and standard messages.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """
    Schema for JWT token response after successful authentication.

    Returned after:
    - Successful login
    - Token refresh
    """

    access_token: str = Field(
        ..., description="JWT access token for API authentication (short-lived: 30 min)"
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token for getting new access tokens (long-lived: 7 days)",
    )
    token_type: str = Field(
        default="bearer", description="Token type for Authorization header"
    )
    expires_in: int = Field(
        default=1800, description="Access token expiration time in seconds (30 minutes)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    }


class UserResponse(BaseModel):
    """
    Schema for user profile response.

    Used in responses that return user information.
    Excludes sensitive data like password_hash.
    """

    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    phone: Optional[str] = Field(None, description="User's phone number")
    role: str = Field(..., description="User role: 'customer' or 'cleaner'")
    profile_pic: Optional[str] = Field(None, description="URL to profile picture")
    is_active: bool = Field(..., description="Whether the account is active")
    email_verified: bool = Field(..., description="Whether email has been verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone": "+919876543210",
                "role": "customer",
                "profile_pic": "https://example.com/pic.jpg",
                "is_active": True,
                "email_verified": False,
                "created_at": "2026-01-31T12:00:00Z",
                "updated_at": "2026-01-31T12:00:00Z",
            }
        }
    }


class UserWithTokenResponse(BaseModel):
    """
    Schema for registration/login response with user data and tokens.
    Combines user info with authentication tokens.
    """

    user: UserResponse = Field(..., description="User profile information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")

    model_config = {
        "json_schema_extra": {
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
                    "created_at": "2026-01-31T12:00:00Z",
                    "updated_at": "2026-01-31T12:00:00Z",
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                },
            }
        }
    }


class MessageResponse(BaseModel):
    """
    Schema for simple message responses.

    Used for:
    - Success confirmations
    - Error messages
    - Status updates
    """

    message: str = Field(..., description="Response message")
    success: bool = Field(
        default=True, description="Whether the operation was successful"
    )

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Operation completed successfully", "success": True}
        }
    }


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    Provides detailed error information.
    """

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "validation_error",
                "message": "Invalid email format",
                "details": {"field": "email", "value": "invalid-email"},
            }
        }
    }
