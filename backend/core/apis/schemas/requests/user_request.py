"""
User Request Schemas
====================
Pydantic models for user profile-related API requests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UpdateProfileRequest(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional - only provided fields will be updated.
    """

    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="User's full name",
        examples=["John Doe"],
    )
    phone: Optional[str] = Field(
        None, description="Contact phone number", examples=["+919876543210"]
    )
    profile_pic: Optional[str] = Field(
        None,
        description="URL to profile picture",
        examples=["https://example.com/profile.jpg"],
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format if provided."""
        if v is None or v == "":
            return None
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return cleaned


class DeleteAccountRequest(BaseModel):
    """
    Schema for account deletion request.
    Requires password confirmation for security.
    """

    password: str = Field(
        ...,
        min_length=1,
        description="Password for confirmation",
        examples=["CurrentPassword123!"],
    )
