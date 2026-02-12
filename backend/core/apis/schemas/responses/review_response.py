"""
Review Response Schemas
=======================
Pydantic models for review API responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReviewResponse(BaseModel):
    """
    Response model for a single review.
    """

    id: str
    booking_id: str
    customer_id: str
    cleaner_id: str

    rating: int
    comment: Optional[str]

    created_at: datetime

    # Enhanced fields (populated if available)
    customer_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """
    Response model for a list of reviews with pagination.
    """

    reviews: List[ReviewResponse]
    total: int
    page: int
    size: int

    avg_rating: float  # Current average for the cleaner
