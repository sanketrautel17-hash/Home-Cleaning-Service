"""
Auth Request Schemas
====================
Pydantic models for authentication-related API requests.
Includes validation for registration, login, and password management.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Validates:
    - Email format
    - Password strength (min 8 chars, uppercase, lowercase, number, special char)
    - Phone format (optional)
    - Role selection
    """

    email: EmailStr = Field(
        ..., description="User's email address", examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must include uppercase, lowercase, number, special char)",
        examples=["SecurePass123!"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name",
        examples=["John Doe"],
    )
    phone: Optional[str] = Field(
        None, description="Contact phone number", examples=["+919876543210"]
    )
    role: str = Field(
        default="customer",
        description="User role: 'customer' or 'cleaner'",
        examples=["customer"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is valid."""
        allowed_roles = ["customer", "cleaner"]
        if v.lower() not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format if provided."""
        if v is None:
            return v
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return cleaned


class UserLoginRequest(BaseModel):
    """
    Schema for user login request.
    """

    email: EmailStr = Field(
        ..., description="User's email address", examples=["user@example.com"]
    )
    password: str = Field(
        ..., min_length=1, description="User's password", examples=["SecurePass123!"]
    )


class ForgotPasswordRequest(BaseModel):
    """
    Schema for forgot password request.
    Initiates password reset flow by sending email.
    """

    email: EmailStr = Field(
        ...,
        description="Email address to send reset link",
        examples=["user@example.com"],
    )


class ResetPasswordRequest(BaseModel):
    """
    Schema for reset password request.
    Used to set new password with reset token.
    """

    token: str = Field(
        ...,
        description="Password reset token from email",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password",
        examples=["NewSecurePass456!"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure new password meets security requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class RefreshTokenRequest(BaseModel):
    """
    Schema for token refresh request.
    Used to get new access token using refresh token.
    """

    refresh_token: str = Field(
        ...,
        description="Refresh token to exchange for new access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing password (authenticated users).
    Requires current password for verification.
    """

    current_password: str = Field(
        ...,
        description="Current password for verification",
        examples=["OldSecurePass123!"],
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password",
        examples=["NewSecurePass456!"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure new password meets security requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
