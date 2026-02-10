"""
Cleaner Request Schemas
=======================
Pydantic models for cleaner profile-related API requests.
Includes validation for profile creation, updates, and search.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class CreateCleanerProfileRequest(BaseModel):
    """
    Schema for creating a cleaner profile.

    Only users with role='cleaner' can create a profile.
    A cleaner can only have ONE profile.

    Validates:
    - Bio length (optional, max 500 chars)
    - Experience years (non-negative)
    - City is required
    - Specializations must be valid categories
    - Location coordinates format
    - Service radius range
    """

    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="Professional bio / about me",
        examples=[
            "Experienced home cleaner with 5+ years in deep cleaning and sanitization."
        ],
    )
    experience_years: int = Field(
        default=0,
        ge=0,
        le=50,
        description="Years of professional cleaning experience",
        examples=[5],
    )
    specializations: Optional[List[str]] = Field(
        None,
        description="List of service categories: regular, deep, move_in_out, office, specialized",
        examples=[["regular", "deep"]],
    )

    # Location fields
    address: Optional[str] = Field(
        None,
        max_length=300,
        description="Full street address",
        examples=["123 Main Street, Andheri West"],
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name (required for search)",
        examples=["Mumbai"],
    )
    state: Optional[str] = Field(
        None,
        max_length=100,
        description="State / province name",
        examples=["Maharashtra"],
    )
    pincode: Optional[str] = Field(
        None,
        max_length=10,
        description="Postal / ZIP code",
        examples=["400058"],
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate",
        examples=[19.0760],
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate",
        examples=[72.8777],
    )
    service_radius_km: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        description="Maximum travel distance in kilometers",
        examples=[15.0],
    )

    @field_validator("specializations")
    @classmethod
    def validate_specializations(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure all specializations are valid categories."""
        if v is None:
            return v
        allowed = {"regular", "deep", "move_in_out", "office", "specialized"}
        for item in v:
            if item.lower() not in allowed:
                raise ValueError(
                    f"Invalid specialization '{item}'. "
                    f"Must be one of: {', '.join(sorted(allowed))}"
                )
        return [item.lower() for item in v]

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        """Validate pincode format if provided."""
        if v is None:
            return v
        cleaned = v.strip()
        if not cleaned.isdigit() or len(cleaned) < 4:
            raise ValueError("Pincode must be a numeric string with at least 4 digits")
        return cleaned


class UpdateCleanerProfileRequest(BaseModel):
    """
    Schema for updating a cleaner profile.
    All fields are optional - only provided fields will be updated.
    """

    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="Professional bio / about me",
        examples=["Updated professional bio text."],
    )
    experience_years: Optional[int] = Field(
        None,
        ge=0,
        le=50,
        description="Years of professional cleaning experience",
        examples=[7],
    )
    specializations: Optional[List[str]] = Field(
        None,
        description="Updated list of specializations",
        examples=[["regular", "deep", "office"]],
    )

    # Location fields
    address: Optional[str] = Field(
        None,
        max_length=300,
        description="Full street address",
        examples=["456 New Street, Bandra East"],
    )
    city: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="City name",
        examples=["Pune"],
    )
    state: Optional[str] = Field(
        None,
        max_length=100,
        description="State / province name",
        examples=["Maharashtra"],
    )
    pincode: Optional[str] = Field(
        None,
        max_length=10,
        description="Postal / ZIP code",
        examples=["411001"],
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate",
        examples=[18.5204],
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate",
        examples=[73.8567],
    )
    service_radius_km: Optional[float] = Field(
        None,
        ge=1.0,
        le=100.0,
        description="Maximum travel distance in kilometers",
        examples=[20.0],
    )
    is_available: Optional[bool] = Field(
        None,
        description="Whether currently accepting new bookings",
        examples=[True],
    )

    @field_validator("specializations")
    @classmethod
    def validate_specializations(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure all specializations are valid categories."""
        if v is None:
            return v
        allowed = {"regular", "deep", "move_in_out", "office", "specialized"}
        for item in v:
            if item.lower() not in allowed:
                raise ValueError(
                    f"Invalid specialization '{item}'. "
                    f"Must be one of: {', '.join(sorted(allowed))}"
                )
        return [item.lower() for item in v]

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        """Validate pincode format if provided."""
        if v is None:
            return v
        cleaned = v.strip()
        if not cleaned.isdigit() or len(cleaned) < 4:
            raise ValueError("Pincode must be a numeric string with at least 4 digits")
        return cleaned
