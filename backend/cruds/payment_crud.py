"""
Payment CRUD Operations
=======================
Database operations for the Payment model.

Handles:
- Creating new payment records
- Updating payment status
- Fetching payments by booking or IDs
"""

from typing import Optional, List
from datetime import datetime
from odmantic import AIOEngine

from models.payment_model import Payment, PaymentStatus
from database.database import get_engine


class PaymentCRUD:
    """
    CRUD operations for payments.
    """

    def __init__(self, engine: Optional[AIOEngine] = None):
        self._engine = engine

    @property
    def engine(self) -> AIOEngine:
        return self._engine or get_engine()

    async def create_payment(
        self,
        booking_id: str,
        customer_id: str,
        amount: float,
        currency: str = "INR",
        method: str = "card",
        transaction_id: str = None,
    ) -> Payment:
        """Create a new payment record."""
        payment = Payment(
            booking_id=booking_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            method=method,
            status=PaymentStatus.PENDING,
            transaction_id=transaction_id,
            created_at=datetime.utcnow(),
        )

        await self.engine.save(payment)
        return payment

    async def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID."""
        # Note: In real app, we use ObjectId, here assuming string ID
        # Since odmantic handles ObjectId/str conversion, we can query by ID directly
        try:
            from bson import ObjectId

            return await self.engine.find_one(
                Payment, Payment.id == ObjectId(payment_id)
            )
        except Exception:
            return None

    async def get_payment_by_booking(self, booking_id: str) -> Optional[Payment]:
        """Get the latest payment for a booking."""
        # A booking may have multiple attempts, we want the most recent or successful one
        # For simplicity, returning the most recent create
        payments = await self.engine.find(
            Payment,
            Payment.booking_id == booking_id,
            sort=Payment.created_at.desc(),
            limit=1,
        )
        return payments[0] if payments else None

    async def get_payment_by_transaction_id(
        self, transaction_id: str
    ) -> Optional[Payment]:
        """Get payment by external transaction ID."""
        return await self.engine.find_one(
            Payment, Payment.transaction_id == transaction_id
        )

    async def update_status(
        self, payment_id: str, status: PaymentStatus, gateway_response: dict = None
    ) -> Optional[Payment]:
        """Update payment status."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return None

        payment.status = status
        if gateway_response:
            payment.gateway_response = gateway_response
        payment.updated_at = datetime.utcnow()

        await self.engine.save(payment)
        return payment


payment_crud = PaymentCRUD()
