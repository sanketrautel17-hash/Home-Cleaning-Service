"""
Review Model
============
Database document model for cleaner reviews in the Home Cleaning Service platform.

A model to store customer reviews for completed bookings.
Linked to:
- Booking (One-to-One: A booking has one review)
- Customer (Who wrote it)
- Cleaner (Who received it)

Technology: ODMantic (MongoDB ODM for FastAPI)
Collection: reviews
"""

from odmantic import Model, Field
from datetime import datetime
from typing import Optional


class Review(Model):
    """
    Review document model.

    Attributes:
        booking_id: ID of the completed booking
        customer_id: User ID of the reviewer
        cleaner_id: User ID of the reviewed cleaner

        rating: 1 to 5 stars
        comment: Text feedback

        created_at: Submission timestamp
    """

    booking_id: str = Field(index=True)
    customer_id: str = Field(index=True)
    cleaner_id: str = Field(index=True)

    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "reviews"}
