"""
Service Request Schemas
=======================
Pydantic models for service package-related API requests.
Includes validation for service creation, updates, and search.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateServiceRequest(BaseModel):
    """
    Schema for creating a new service package.

    Only users with role='cleaner' can create services.

    Validates:
    - Name length (3-100 chars)
    - Category is a valid cleaning type
    - Price is non-negative
    - Price type is valid
    - Duration is within reasonable bounds
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Service display name",
        examples=["Premium Deep Cleaning"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of what's included",
        examples=[
            "Complete deep cleaning including kitchen, bathrooms, and all rooms. Includes scrubbing, sanitization, and deodorizing."
        ],
    )
    category: str = Field(
        default="regular",
        description="Service category: regular, deep, move_in_out, office, specialized",
        examples=["deep"],
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Base price amount",
        examples=[1500.0],
    )
    price_type: str = Field(
        default="flat",
        description="Pricing model: flat, per_hour, per_sqft",
        examples=["flat"],
    )
    duration_hours: float = Field(
        default=1.0,
        ge=0.5,
        le=24.0,
        description="Estimated time to complete (in hours)",
        examples=[3.0],
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Ensure category is a valid cleaning type."""
        allowed = {"regular", "deep", "move_in_out", "office", "specialized"}
        if v.lower() not in allowed:
            raise ValueError(
                f"Invalid category '{v}'. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()

    @field_validator("price_type")
    @classmethod
    def validate_price_type(cls, v: str) -> str:
        """Ensure price type is valid."""
        allowed = {"flat", "per_hour", "per_sqft"}
        if v.lower() not in allowed:
            raise ValueError(
                f"Invalid price type '{v}'. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()


class UpdateServiceRequest(BaseModel):
    """
    Schema for updating a service package.
    All fields are optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Service display name",
        examples=["Updated Service Name"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated description",
        examples=["Updated service description with new details."],
    )
    category: Optional[str] = Field(
        None,
        description="Service category: regular, deep, move_in_out, office, specialized",
        examples=["office"],
    )
    price: Optional[float] = Field(
        None,
        ge=0.0,
        description="Updated base price",
        examples=[2000.0],
    )
    price_type: Optional[str] = Field(
        None,
        description="Updated pricing model: flat, per_hour, per_sqft",
        examples=["per_hour"],
    )
    duration_hours: Optional[float] = Field(
        None,
        ge=0.5,
        le=24.0,
        description="Updated estimated time (in hours)",
        examples=[4.0],
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether to activate or deactivate this service",
        examples=[True],
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Ensure category is a valid cleaning type."""
        if v is None:
            return v
        allowed = {"regular", "deep", "move_in_out", "office", "specialized"}
        if v.lower() not in allowed:
            raise ValueError(
                f"Invalid category '{v}'. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()

    @field_validator("price_type")
    @classmethod
    def validate_price_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure price type is valid."""
        if v is None:
            return v
        allowed = {"flat", "per_hour", "per_sqft"}
        if v.lower() not in allowed:
            raise ValueError(
                f"Invalid price type '{v}'. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()
