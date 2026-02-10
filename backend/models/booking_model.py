"""
Booking Model
=============
Database document model for service bookings in the Home Cleaning Service platform.

Tracks the entire lifecycle of a service request:
Draft -> Pending -> Confirmed -> In Progress -> Completed (or Cancelled)

Technology: ODMantic (MongoDB ODM for FastAPI)
Collection: bookings
"""

from odmantic import Model, Field, EmbeddedModel
from datetime import datetime
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    """
    Status of a booking in its lifecycle.

    - PENDING: Created by customer, waiting for cleaner acceptance
    - CONFIRMED: Accepted by cleaner
    - IN_PROGRESS: Cleaner has started the job
    - COMPLETED: Job finished successfully
    - CANCELLED: Cancelled by customer or cleaner
    - REJECTED: Rejected by cleaner
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PaymentStatus(str, Enum):
    """Payment status for the booking."""

    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"


class BookingAddress(EmbeddedModel):
    """Physical address where service will be performed."""

    street: str
    city: str
    state: str
    pincode: str

    # Optional coordinates for verifying location
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Booking(Model):
    """
    Booking document model.

    Relationships:
    - customer_id -> users collection
    - cleaner_id -> users collection (NOT cleaner_profiles, use user_id)
    - service_id -> services collection

    Attributes:
        customer_id: User ID of the customer
        cleaner_id: User ID of the cleaner
        service_id: ID of the service package

        scheduled_date: Date of service (YYYY-MM-DD)
        start_time: Start time (HH:MM)
        duration_hours: Expected duration

        total_price: Final price (Service Price + Platform Fee)
        platform_fee: Fee retained by platform

        status: Current booking status
        address: Service location
        instructions: Special notes from customer
    """

    # ==========================================================================
    # References
    # ==========================================================================
    customer_id: str = Field(index=True)
    cleaner_id: str = Field(index=True)
    service_id: str = Field(index=True)

    # ==========================================================================
    # Schedule
    # ==========================================================================
    scheduled_date: datetime = Field(index=True)  # Store as datetime for querying
    start_time: str  # Format: "HH:MM"
    duration_hours: float

    # ==========================================================================
    # Financials (Snapshot at time of booking)
    # ==========================================================================
    service_price: float
    platform_fee: float
    total_price: float
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    # ==========================================================================
    # Details
    # ==========================================================================
    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)
    address: BookingAddress
    special_instructions: Optional[str] = None

    # Cancellation details
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None  # User ID who cancelled

    # ==========================================================================
    # Timestamps
    # ==========================================================================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "bookings"}

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    @property
    def end_time(self) -> str:
        """Helper to calculate end time based on start_time and duration."""
        # Simple implementation, can be expanded
        try:
            h, m = map(int, self.start_time.split(":"))
            total_minutes = h * 60 + m + int(self.duration_hours * 60)
            end_h = (total_minutes // 60) % 24
            end_m = total_minutes % 60
            return f"{end_h:02d}:{end_m:02d}"
        except:
            return ""
