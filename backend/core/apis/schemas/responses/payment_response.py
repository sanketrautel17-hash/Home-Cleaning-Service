"""
Payment Response Schemas
========================
Pydantic models for payment API responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PaymentResponse(BaseModel):
    """
    Response model for a payment transaction.
    """

    id: str
    booking_id: str
    customer_id: str

    amount: float
    currency: str
    status: str
    method: str

    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    """
    Simple status check response.
    """

    payment_id: str
    status: str
    booking_paid: bool
