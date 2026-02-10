"""
Cleaner Profile Model
=====================
Database document model for cleaner professional profiles in the
Home Cleaning Service platform.

Each user with role='cleaner' can have ONE extended profile containing
professional details, service area, availability, and performance stats.

Technology: ODMantic (MongoDB ODM for FastAPI)
Collection: cleaner_profiles
"""

from odmantic import Model, EmbeddedModel, Field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class ServiceCategory(str, Enum):
    """
    Categories of cleaning services a cleaner can specialize in.

    - REGULAR: Standard home cleaning (sweeping, mopping, dusting)
    - DEEP: Deep cleaning (behind appliances, inside cabinets, etc.)
    - MOVE_IN_OUT: Move-in/move-out cleaning for tenants
    - OFFICE: Commercial/office space cleaning
    - SPECIALIZED: Specialized cleaning (carpet, upholstery, post-construction)
    """

    REGULAR = "regular"
    DEEP = "deep"
    MOVE_IN_OUT = "move_in_out"
    OFFICE = "office"
    SPECIALIZED = "specialized"


class Location(EmbeddedModel):
    """
    Embedded model for GeoJSON Point location.

    MongoDB uses GeoJSON format for geospatial queries.
    Format: { "type": "Point", "coordinates": [longitude, latitude] }

    Note: MongoDB expects [longitude, latitude] order (not lat, lng).
    """

    type: str = Field(default="Point")
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])


class CleanerProfile(Model):
    """
    Cleaner professional profile document model.

    This is an EXTENSION of the User model — every cleaner has one User
    record (for auth) and one CleanerProfile record (for professional info).

    Relationship: One-to-One with User (via user_id)

    Attributes:
        user_id: Reference to the User document (unique, indexed)
        bio: Professional bio / about me text
        experience_years: Years of professional cleaning experience
        specializations: List of service categories they specialize in

        address: Full street address (private, not shown publicly)
        city: City name for search/filtering (indexed)
        state: State/province name
        pincode: Postal/ZIP code
        location: GeoJSON Point for location-based "nearby" search
        service_radius_km: Maximum travel distance from base location

        is_available: Whether currently accepting new bookings
        avg_rating: Computed average star rating (0.0 - 5.0)
        total_reviews: Total number of reviews received
        completed_jobs: Number of successfully completed bookings
        verified: Whether profile has been admin-verified

        created_at: Profile creation timestamp
        updated_at: Last profile update timestamp
    """

    # ==========================================================================
    # User Reference (One-to-One)
    # ==========================================================================
    user_id: str = Field(unique=True, index=True)

    # ==========================================================================
    # Professional Info
    # ==========================================================================
    bio: Optional[str] = None
    experience_years: int = Field(default=0, ge=0)
    specializations: List[str] = Field(
        default_factory=lambda: [ServiceCategory.REGULAR.value]
    )

    # ==========================================================================
    # Location & Service Area
    # ==========================================================================
    address: Optional[str] = None
    city: str = Field(default="", index=True)
    state: Optional[str] = None
    pincode: Optional[str] = None
    location: Optional[Dict] = None  # GeoJSON Point for geo queries
    service_radius_km: float = Field(default=10.0, ge=1.0, le=100.0)

    # ==========================================================================
    # Availability & Status
    # ==========================================================================
    is_available: bool = Field(default=True, index=True)
    verified: bool = Field(default=False)

    # ==========================================================================
    # Performance Stats (updated by other phases)
    # ==========================================================================
    avg_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0, ge=0)
    completed_jobs: int = Field(default=0, ge=0)

    # ==========================================================================
    # Timestamps
    # ==========================================================================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "cleaner_profiles"}

    def update_timestamp(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    def update_rating(self, new_avg: float, total: int):
        """
        Update rating stats after a new review is submitted.

        Args:
            new_avg: Newly calculated average rating
            total: New total review count
        """
        self.avg_rating = round(new_avg, 2)
        self.total_reviews = total
        self.update_timestamp()

    def increment_completed_jobs(self):
        """Increment the completed jobs counter after a booking is fulfilled."""
        self.completed_jobs += 1
        self.update_timestamp()

    def __repr__(self) -> str:
        return (
            f"CleanerProfile(user_id={self.user_id}, "
            f"city={self.city}, available={self.is_available})"
        )
