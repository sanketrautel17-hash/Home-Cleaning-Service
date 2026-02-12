"""
Payment Request Schemas
=======================
Pydantic models for payment API requests.
"""

from pydantic import BaseModel, Field
from typing import Optional


class InitiatePaymentRequest(BaseModel):
    """
    Schema to start a payment process for a booking.

    The user provides the booking ID and optionally the payment method.
    The amount is automatically calculated from the booking details.
    """

    booking_id: str = Field(..., description="ID of the booking to pay for")
    method: str = Field("card", description="Payment method: card, upi, etc.")


class PaymentWebhookRequest(BaseModel):
    """
    Schema for mock webhook callback to confirm payment status.
    In real integration, this would match Stripe/Razorpay payload.
    """

    payment_id: str
    status: str
    transaction_id: str
