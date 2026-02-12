"""
Review CRUD Operations
======================
Database operations for the Review model.

Handles:
- Creating new reviews
- Getting reviews for a specific cleaner
- Calculating aggregate stats (average rating, review count)
"""

from typing import List, Tuple, Optional
from datetime import datetime
from odmantic import AIOEngine

from models.review_model import Review
from database.database import get_engine


class ReviewCRUD:
    """
    CRUD operations for reviews.
    """

    def __init__(self, engine: Optional[AIOEngine] = None):
        self._engine = engine

    @property
    def engine(self) -> AIOEngine:
        return self._engine or get_engine()

    async def create_review(
        self,
        booking_id: str,
        customer_id: str,
        cleaner_id: str,
        rating: int,
        comment: Optional[str] = None,
    ) -> Review:
        """Create and save a new review."""
        review = Review(
            booking_id=booking_id,
            customer_id=customer_id,
            cleaner_id=cleaner_id,
            rating=rating,
            comment=comment,
            created_at=datetime.utcnow(),
        )

        await self.engine.save(review)
        return review

    async def get_reviews_by_cleaner(
        self, cleaner_id: str, skip: int = 0, limit: int = 20
    ) -> List[Review]:
        """Get paginated reviews for a cleaner, sorted by newest."""
        reviews = await self.engine.find(
            Review,
            Review.cleaner_id == cleaner_id,
            sort=Review.created_at.desc(),
            skip=skip,
            limit=limit,
        )
        return reviews

    async def get_total_reviews(self, cleaner_id: str) -> int:
        """Count total reviews for a cleaner."""
        return await self.engine.count(Review, Review.cleaner_id == cleaner_id)

    async def get_cleaner_stats(self, cleaner_id: str) -> Tuple[float, int]:
        """
        Calculate cleaner stats: (average_rating, total_reviews).

        Note: This executes a full scan aggregation. In production with millions
        of reviews, we would cache this or update incrementally on write.
        """
        # Get all reviews for calculation (for MVP scale)
        # TODO: Use MongoDB aggregation pipeline for better performance at scale
        reviews = await self.engine.find(Review, Review.cleaner_id == cleaner_id)

        count = len(reviews)
        if count == 0:
            return 0.0, 0

        total_score = sum(r.rating for r in reviews)
        # Round to 1 decimal place
        avg = round(total_score / count, 1)

        return avg, count

    async def get_review_by_booking(self, booking_id: str) -> Optional[Review]:
        """Check if a booking already has a review."""
        return await self.engine.find_one(Review, Review.booking_id == booking_id)


# Singleton instance
review_crud = ReviewCRUD()
