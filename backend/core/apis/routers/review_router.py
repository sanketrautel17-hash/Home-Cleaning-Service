"""
Review Router
=============
FastAPI routes for review management.
Prefix: /api/reviews
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Any

from controllers.review_controller import review_controller
from commons.dependencies import require_customer, get_current_user
from models.user_model import User
from core.apis.schemas.requests.review_request import CreateReviewRequest
from core.apis.schemas.responses.review_response import (
    ReviewResponse,
    ReviewListResponse,
)

router = APIRouter(
    prefix="/api/reviews",
    tags=["Reviews"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review",
    description="Submit a review for a completed booking. Only customers can review.",
)
async def create_review(
    request: CreateReviewRequest,
    current_user: User = Depends(require_customer),
):
    """
    Create a new review.

    Requirements:
    - User must be the customer of the booking
    - Booking must be COMPLETED
    - One review per booking
    """
    return await review_controller.create_review(
        customer_id=str(current_user.id),
        booking_id=request.booking_id,
        rating=request.rating,
        comment=request.comment,
    )


@router.get(
    "/cleaner/{cleaner_id}",
    response_model=ReviewListResponse,
    summary="Get cleaner reviews",
    description="Get public reviews for a specific cleaner.",
)
async def get_cleaner_reviews(
    cleaner_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    """
    Get reviews for a cleaner.
    No authentication required.
    """
    return await review_controller.get_cleaner_reviews(
        cleaner_id=cleaner_id,
        skip=skip,
        limit=limit,
    )
