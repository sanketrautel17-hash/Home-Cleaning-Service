"""
Booking Controller
==================
Business logic for booking operations.
Handles availability checks, pricing, and status transitions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from fastapi import HTTPException, status

from cruds.booking_crud import booking_crud
from cruds.service_crud import service_crud
from cruds.user_crud import user_crud
from models.user_model import User, UserRole
from models.booking_model import BookingStatus

# Platform configuration
PLATFORM_FEE_PERCENTAGE = 0.10  # 10% fee


class BookingController:
    """
    Booking business logic controller.
    """

    async def create_booking(
        self,
        customer_id: str,
        service_id: str,
        cleaner_id: str,
        scheduled_date: date,
        start_time: str,
        address: dict,
        special_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new booking.
        """
        # 1. Verify Service matches Cleaner
        service = await service_crud.get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        if service.cleaner_id != cleaner_id:
            raise HTTPException(
                status_code=400, detail="Service does not belong to this cleaner"
            )

        if not service.is_active:
            raise HTTPException(
                status_code=400, detail="Service is not currently active"
            )

        # 2. Check Availability
        # Convert date to datetime for availability check
        sched_dt = datetime.combine(scheduled_date, datetime.min.time())

        is_available = await booking_crud.check_cleaner_availability(
            cleaner_id=cleaner_id,
            date=sched_dt,
            start_time=start_time,
            duration_hours=service.duration_hours,
        )

        if not is_available:
            raise HTTPException(
                status_code=409,
                detail="Cleaner is not available at this time. Please choose another slot.",
            )

        # 3. Calculate Pricing
        service_price = service.price
        platform_fee = service_price * PLATFORM_FEE_PERCENTAGE

        # 4. Create Booking
        booking = await booking_crud.create_booking(
            customer_id=customer_id,
            cleaner_id=cleaner_id,
            service_id=service_id,
            scheduled_date=sched_dt,
            start_time=start_time,
            duration_hours=service.duration_hours,
            service_price=service_price,
            platform_fee=platform_fee,
            address=address,
            special_instructions=special_instructions,
        )

        return self._booking_to_dict(booking)

    async def get_my_bookings(
        self, user: User, skip: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get bookings for the current user."""

        if user.role == UserRole.CUSTOMER:
            bookings = await booking_crud.get_customer_bookings(
                customer_id=str(user.id), skip=skip, limit=limit, status=status
            )
        else:
            bookings = await booking_crud.get_cleaner_bookings(
                cleaner_id=str(user.id), skip=skip, limit=limit, status=status
            )

        bookings_data = [self._booking_to_dict(b) for b in bookings]

        # TODO: Enhance bookings with related entity names (Customer/Cleaner name)
        # For now, return raw bookings
        return {
            "bookings": bookings_data,
            "total": len(bookings),  # improved: count properly in CRUD later
            "page": (skip // limit) + 1,
            "size": limit,
        }

    async def update_status(
        self, booking_id: str, new_status: str, user: User, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update booking status with permission checks.
        """
        booking = await booking_crud.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Permission logic
        is_cleaner = booking.cleaner_id == str(user.id)
        is_customer = booking.customer_id == str(user.id)

        if not (is_cleaner or is_customer):
            raise HTTPException(
                status_code=403, detail="Not authorized to update this booking"
            )

        # State transitions
        if new_status == BookingStatus.CONFIRMED:
            if not is_cleaner:
                raise HTTPException(
                    status_code=403, detail="Only cleaner can confirm booking"
                )
            if booking.status != BookingStatus.PENDING:
                raise HTTPException(
                    status_code=400, detail="Can only confirm pending bookings"
                )

        elif new_status == BookingStatus.REJECTED:
            if not is_cleaner:
                raise HTTPException(
                    status_code=403, detail="Only cleaner can reject booking"
                )
            if booking.status != BookingStatus.PENDING:
                raise HTTPException(
                    status_code=400, detail="Can only reject pending bookings"
                )

        elif new_status == BookingStatus.CANCELLED:
            # Both can cancel, but typically restrictions apply (e.g. 24h notice)
            pass

        elif new_status == BookingStatus.COMPLETED:
            if not is_cleaner:
                raise HTTPException(
                    status_code=403, detail="Only cleaner can complete booking"
                )
            if (
                booking.status != BookingStatus.IN_PROGRESS
                and booking.status != BookingStatus.CONFIRMED
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Booking must be confirmed or in progress to complete",
                )

        # Apply Update
        updated_booking = await booking_crud.update_booking_status(
            booking_id=booking_id,
            new_status=new_status,
            user_id=str(user.id),
            reason=reason,
        )

        if not updated_booking:
            raise HTTPException(
                status_code=500, detail="Failed to update booking status"
            )

        return self._booking_to_dict(updated_booking)

    def _booking_to_dict(self, booking: Any) -> Dict[str, Any]:
        """Convert Booking object to dictionary for API response."""
        return {
            "id": str(booking.id),
            "customer_id": booking.customer_id,
            "cleaner_id": booking.cleaner_id,
            "service_id": booking.service_id,
            "scheduled_date": booking.scheduled_date.date(),
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "duration_hours": booking.duration_hours,
            "status": booking.status.value,
            "payment_status": booking.payment_status.value,
            "total_price": booking.total_price,
            "service_price": booking.service_price,
            "platform_fee": booking.platform_fee,
            "address": booking.address.model_dump(),
            "special_instructions": booking.special_instructions,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
        }


booking_controller = BookingController()
