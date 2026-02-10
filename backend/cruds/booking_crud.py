"""
Booking CRUD Operations
=======================
Database operations for Booking model using ODMantic.
Handles booking creation, retrieval, and status updates.
"""

from typing import List, Optional
from datetime import datetime, time
from bson import ObjectId
from odmantic import AIOEngine

from models.booking_model import Booking, BookingStatus, BookingAddress
from database.database import get_engine


class BookingCRUD:
    """
    CRUD operations for Booking model.
    """

    def __init__(self, engine: Optional[AIOEngine] = None):
        """Initialize with optional custom engine."""
        self._engine = engine

    @property
    def engine(self) -> AIOEngine:
        """Get the ODMantic engine."""
        return self._engine or get_engine()

    # =========================================================================
    # CREATE Operations
    # =========================================================================

    async def create_booking(
        self,
        customer_id: str,
        cleaner_id: str,
        service_id: str,
        scheduled_date: datetime,
        start_time: str,
        duration_hours: float,
        service_price: float,
        platform_fee: float,
        address: dict,
        special_instructions: Optional[str] = None,
    ) -> Booking:
        """Create a new booking."""

        total_price = service_price + platform_fee

        # Create address embedded model
        booking_address = BookingAddress(
            street=address.get("street", ""),
            city=address.get("city", ""),
            state=address.get("state", ""),
            pincode=address.get("pincode", ""),
            latitude=address.get("latitude"),
            longitude=address.get("longitude"),
        )

        booking = Booking(
            customer_id=customer_id,
            cleaner_id=cleaner_id,
            service_id=service_id,
            scheduled_date=scheduled_date,
            start_time=start_time,
            duration_hours=duration_hours,
            service_price=service_price,
            platform_fee=platform_fee,
            total_price=total_price,
            status=BookingStatus.PENDING,
            address=booking_address,
            special_instructions=special_instructions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        await self.engine.save(booking)
        return booking

    # =========================================================================
    # READ Operations
    # =========================================================================

    async def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get a booking by its ID."""
        try:
            return await self.engine.find_one(
                Booking, Booking.id == ObjectId(booking_id)
            )
        except Exception:
            return None

    async def get_customer_bookings(
        self,
        customer_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> List[Booking]:
        """Get all bookings for a customer."""
        filters = [Booking.customer_id == customer_id]
        if status:
            filters.append(Booking.status == status)

        bookings = await self.engine.find(
            Booking,
            *filters,
            sort=Booking.scheduled_date.desc(),
            skip=skip,
            limit=limit
        )
        return bookings

    async def get_cleaner_bookings(
        self,
        cleaner_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> List[Booking]:
        """Get all bookings for a cleaner (schedule)."""
        filters = [Booking.cleaner_id == cleaner_id]
        if status:
            filters.append(Booking.status == status)

        bookings = await self.engine.find(
            Booking,
            *filters,
            sort=Booking.scheduled_date.desc(),
            skip=skip,
            limit=limit
        )
        return bookings

    async def check_cleaner_availability(
        self, cleaner_id: str, date: datetime, start_time: str, duration_hours: float
    ) -> bool:
        """
        Check if a cleaner is available at specific date/time.
        Returns True if available, False if already booked.
        """
        # Find all confirmed or pending bookings for this cleaner on this date
        # Note: We query strictly by date first for performance
        # Using >= date and < date+1day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        bookings = await self.engine.find(
            Booking,
            Booking.cleaner_id == cleaner_id,
            Booking.scheduled_date >= start_of_day,
            Booking.scheduled_date <= end_of_day,
            Booking.status.in_(
                [
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                    BookingStatus.IN_PROGRESS,
                ]
            ),
        )

        # Simple time overlap check
        # Convert times to float hours for easier comparison (e.g., "14:30" -> 14.5)
        def time_to_float(t_str: str) -> float:
            h, m = map(int, t_str.split(":"))
            return h + m / 60.0

        new_start = time_to_float(start_time)
        new_end = new_start + duration_hours

        for booking in bookings:
            existing_start = time_to_float(booking.start_time)
            existing_end = existing_start + booking.duration_hours

            # Check for overlap
            # Overlap logic: (StartA < EndB) and (EndA > StartB)
            if new_start < existing_end and new_end > existing_start:
                return False  # Overlap found, not available

        return True

    # =========================================================================
    # UPDATE Operations
    # =========================================================================

    async def update_booking_status(
        self,
        booking_id: str,
        new_status: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Optional[Booking]:
        """Update booking status (e.g., confirm, cancel)."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None

        booking.status = new_status
        booking.updated_at = datetime.utcnow()

        if new_status == BookingStatus.CANCELLED and user_id:
            booking.cancelled_by = user_id
            booking.cancellation_reason = reason

        await self.engine.save(booking)
        return booking


# Create singleton instance
booking_crud = BookingCRUD()
