"""
Service Package Model
=====================
Database document model for cleaning service packages offered by cleaners
in the Home Cleaning Service platform.

Each cleaner can offer multiple service packages (like a menu).
Customers browse and select a service package when making a booking.

Technology: ODMantic (MongoDB ODM for FastAPI)
Collection: services
"""

from odmantic import Model, Field
from datetime import datetime
from typing import Optional
from enum import Enum

from models.cleaner_profile_model import ServiceCategory


class PriceType(str, Enum):
    """
    How the service price is calculated.

    - FLAT: Fixed price for the entire service (e.g., ₹1500 for deep cleaning)
    - PER_HOUR: Charged per hour (e.g., ₹300/hour)
    - PER_SQFT: Charged per square foot (e.g., ₹5/sqft for large spaces)
    """

    FLAT = "flat"
    PER_HOUR = "per_hour"
    PER_SQFT = "per_sqft"


class ServicePackage(Model):
    """
    Cleaning service package offered by a cleaner.

    Each cleaner can create multiple service packages with different
    categories, pricing, and descriptions. Customers view these when
    browsing a cleaner's profile or searching for services.

    Relationship: Many-to-One with User/CleanerProfile (via cleaner_id)

    Attributes:
        cleaner_id: Reference to the User who offers this service (indexed)
        name: Service display name (e.g., "Premium Deep Cleaning")
        description: Detailed description of what's included
        category: Type of cleaning service (from ServiceCategory enum)
        price: Base price amount
        price_type: How pricing is calculated (flat, per_hour, per_sqft)
        duration_hours: Estimated time to complete the service
        is_active: Whether this service is currently available for booking
        created_at: Service creation timestamp
        updated_at: Last update timestamp
    """

    # ==========================================================================
    # Cleaner Reference (Many-to-One)
    # ==========================================================================
    cleaner_id: str = Field(index=True)

    # ==========================================================================
    # Service Details
    # ==========================================================================
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    category: ServiceCategory = Field(default=ServiceCategory.REGULAR, index=True)

    # ==========================================================================
    # Pricing
    # ==========================================================================
    price: float = Field(ge=0.0)
    price_type: PriceType = Field(default=PriceType.FLAT)
    duration_hours: float = Field(default=1.0, ge=0.5, le=24.0)

    # ==========================================================================
    # Status
    # ==========================================================================
    is_active: bool = Field(default=True, index=True)

    # ==========================================================================
    # Timestamps
    # ==========================================================================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "services"}

    def update_timestamp(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"ServicePackage(name={self.name}, "
            f"category={self.category.value}, price={self.price})"
        )
