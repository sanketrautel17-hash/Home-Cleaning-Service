"""
Review Request Schemas
======================
Pydantic models for review submission API.
"""

from pydantic import BaseModel, Field
from typing import Optional


class CreateReviewRequest(BaseModel):
    """
    Schema for creating a new review.

    A review is linked to a specific completed booking.

    Constraints:
    - rating: 1 to 5 stars
    - comment: Optional text feedback (max 1000 chars)
    """

    booking_id: str = Field(..., description="ID of the completed booking")
    rating: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    comment: Optional[str] = Field(
        None, max_length=1000, description="Optional feedback text"
    )
