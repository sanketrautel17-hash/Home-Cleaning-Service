"""
Review Controller
=================
Business logic for review operations.

Handles:
- Review submission (with permission & status checks)
- Updating cleaner profiles with new rating stats
- Review search & listing
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status

from cruds.review_crud import review_crud
from cruds.booking_crud import booking_crud
from cruds.cleaner_crud import cleaner_crud
from cruds.user_crud import user_crud
from models.user_model import User, UserRole
from models.booking_model import BookingStatus


class ReviewController:
    """
    Review business logic controller.
    """

    async def create_review(
        self,
        customer_id: str,
        booking_id: str,
        rating: int,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit a new review for a booking.

        Rules:
        1. Booking must exist
        2. User must be the customer of the booking
        3. Booking status must be COMPLETED
        4. Booking must not already have a review
        5. After review, update cleaner's profile stats
        """

        # 1. Fetch Booking
        booking = await booking_crud.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        # 2. Permission Check
        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review your own bookings",
            )

        # 3. Status Check
        if booking.status != BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only review completed bookings",
            )

        # 4. Duplicate Check
        existing_review = await review_crud.get_review_by_booking(booking_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this booking",
            )

        # Create Review
        review = await review_crud.create_review(
            booking_id=booking_id,
            customer_id=customer_id,
            cleaner_id=booking.cleaner_id,
            rating=rating,
            comment=comment,
        )

        # 5. Update Cleaner Profile Stats
        # This is CRITICAL for search ranking
        await self._update_cleaner_stats(booking.cleaner_id)

        return self._review_to_dict(review)

    async def get_cleaner_reviews(
        self, cleaner_id: str, skip: int = 0, limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get public reviews for a cleaner.
        """
        reviews = await review_crud.get_reviews_by_cleaner(
            cleaner_id=cleaner_id, skip=skip, limit=limit
        )

        total = await review_crud.get_total_reviews(cleaner_id)

        # Enrich reviews with customer names
        reviews_data = []
        for r in reviews:
            data = self._review_to_dict(r)
            customer = await user_crud.get_user_by_id(r.customer_id)
            if customer:
                # Only show first name for privacy? Or full name?
                # For now, full name
                data["customer_name"] = customer.full_name
            reviews_data.append(data)

        # Get current stats (for avg_rating)
        avg_rating, _ = await review_crud.get_cleaner_stats(cleaner_id)

        return {
            "reviews": reviews_data,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "avg_rating": avg_rating,
        }

    async def _update_cleaner_stats(self, cleaner_id: str):
        """
        Recalculate and update cleaner's profile ratings.
        """
        avg_rating, total_reviews = await review_crud.get_cleaner_stats(cleaner_id)

        # Update using specific method for ratings
        await cleaner_crud.update_rating(
            user_id=cleaner_id, new_avg=avg_rating, total_reviews=total_reviews
        )

    def _review_to_dict(self, review: Any) -> Dict[str, Any]:
        """Convert Review object to dictionary."""
        return {
            "id": str(review.id),
            "booking_id": review.booking_id,
            "customer_id": review.customer_id,
            "cleaner_id": review.cleaner_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
        }


review_controller = ReviewController()
