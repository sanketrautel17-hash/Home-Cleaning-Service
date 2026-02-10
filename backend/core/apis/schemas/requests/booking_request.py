from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date


class BookingAddressRequest(BaseModel):
    street: str = Field(..., min_length=5, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    pincode: str = Field(..., min_length=6, max_length=6)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CreateBookingRequest(BaseModel):
    service_id: str = Field(..., description="ID of the service package to book")
    cleaner_id: str = Field(..., description="ID of the cleaner offering the service")
    scheduled_date: date = Field(..., description="Date of the booking (YYYY-MM-DD)")
    start_time: str = Field(
        ...,
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Start time in HH:MM format",
    )
    address: BookingAddressRequest
    special_instructions: Optional[str] = Field(None, max_length=500)

    @validator("scheduled_date")
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError("Booking date cannot be in the past")
        return v


class UpdateBookingStatusRequest(BaseModel):
    status: str = Field(..., description="New status for the booking")
    reason: Optional[str] = Field(None, description="Reason for cancellation/rejection")
