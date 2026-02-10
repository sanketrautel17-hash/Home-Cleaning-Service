"""
Booking Router
==============
FastAPI routes for booking management.
Prefix: /api/bookings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from controllers.booking_controller import booking_controller
from commons.dependencies import get_current_user, require_customer
from models.user_model import User, UserRole
from core.apis.schemas.requests.booking_request import (
    CreateBookingRequest,
    UpdateBookingStatusRequest,
)
from core.apis.schemas.responses.booking_response import (
    BookingBaseResponse,
    BookingListResponse,
)

router = APIRouter(
    prefix="/api/bookings",
    tags=["Bookings"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=BookingBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book a service",
    description="Customer creates a new booking request.",
)
async def create_booking(
    request: CreateBookingRequest, current_user: User = Depends(require_customer)
):
    """
    Create a new booking.
    Only customers can create bookings.
    """
    return await booking_controller.create_booking(
        customer_id=str(current_user.id),
        service_id=request.service_id,
        cleaner_id=request.cleaner_id,
        scheduled_date=request.scheduled_date,
        start_time=request.start_time,
        address=request.address.dict(),
        special_instructions=request.special_instructions,
    )


@router.get(
    "",
    response_model=BookingListResponse,
    summary="Get my bookings",
    description="Get list of bookings for the current user (Customer or Cleaner).",
)
async def get_bookings(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get all bookings for the authenticated user.
    """
    result = await booking_controller.get_my_bookings(
        user=current_user, skip=skip, limit=limit, status=status
    )

    # Transform raw Booking models to response schema
    # (Assuming controller returns dict with 'bookings' list)
    return result


@router.patch(
    "/{booking_id}/status",
    response_model=BookingBaseResponse,
    summary="Update booking status",
    description="Update the status of a booking (e.g., Confirm, Cancel).",
)
async def update_booking_status(
    booking_id: str,
    request: UpdateBookingStatusRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Update booking status.
    Cleaners can: Confirm, Reject, Complete.
    Customers can: Cancel.
    """
    return await booking_controller.update_status(
        booking_id=booking_id,
        new_status=request.status,
        user=current_user,
        reason=request.reason,
    )
