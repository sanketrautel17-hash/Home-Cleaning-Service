"""
Payment Model
=============
Database document model for financial transactions.

Handles tracking of payments made by customers for bookings.
Linked to:
- Booking (One-to-Many: A booking could have multiple payment attempts, but one successful one)
- Customer (Payer)
- Cleaner (Payee - indirectly, platform pays them)

Technology: ODMantic (MongoDB ODM)
Collection: payments
"""

from odmantic import Model, Field
from datetime import datetime
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    """Status of a payment transaction."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Supported payment methods."""

    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    CASH = "cash"  # Cash on delivery/completion


class Payment(Model):
    """
    Payment document model.

    Attributes:
        booking_id: ID of the booking being paid for
        customer_id: ID of the user making the payment

        amount: Amount in base currency (e.g., INR, USD)
        currency: 3-letter currency code (default: INR)

        status: Current status of the transaction
        method: Payment method used

        transaction_id: External gateway transaction ID (e.g., Stripe/Razorpay ID)
        gateway_response: Raw response from payment gateway (optional, for logs)

        created_at: When the payment was initiated
        updated_at: Last status update time
    """

    booking_id: str = Field(index=True)
    customer_id: str = Field(index=True)

    amount: float = Field(ge=0)
    currency: str = Field(default="INR")

    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    method: PaymentMethod = Field(default=PaymentMethod.CARD)

    transaction_id: Optional[str] = Field(None, index=True)
    gateway_response: Optional[dict] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "payments"}
