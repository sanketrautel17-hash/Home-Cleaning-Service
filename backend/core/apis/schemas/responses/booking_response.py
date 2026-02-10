from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from uuid import UUID


class BookingAddressResponse(BaseModel):
    street: str
    city: str
    state: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BookingBaseResponse(BaseModel):
    id: str
    customer_id: str
    cleaner_id: str
    service_id: str

    scheduled_date: date
    start_time: str
    duration_hours: float
    end_time: str

    total_price: float
    status: str
    payment_status: str

    address: BookingAddressResponse
    special_instructions: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnhancedBookingResponse(BookingBaseResponse):
    """
    Enhanced response with related details.
    Ideally, we would join Customer, Cleaner, and Service details here.
    """

    customer_name: Optional[str] = None
    cleaner_name: Optional[str] = None
    service_name: Optional[str] = None


class BookingListResponse(BaseModel):
    bookings: List[EnhancedBookingResponse]
    total: int
    page: int
    size: int
