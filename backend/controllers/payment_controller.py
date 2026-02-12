"""
Payment Controller
==================
Business logic for payment processing.

Handles:
- Initiating payment for bookings
- Processing Mock Payment Gateway webhooks/verifications
- Updating Booking payment status
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from cruds.booking_crud import booking_crud
from cruds.payment_crud import payment_crud
from services.payment_service import payment_service
from models.booking_model import BookingStatus, PaymentStatus
from models.payment_model import PaymentStatus as TransactionStatus


class PaymentController:
    """
    Payment business logic controller.
    """

    async def initiate_payment(
        self, customer_id: str, booking_id: str, method: str = "card"
    ) -> Dict[str, Any]:
        """
        Start a payment transaction for a booking.
        """
        # 1. Fetch Booking
        booking = await booking_crud.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        # 2. Permission Check
        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only pay for your own bookings",
            )

        # 3. Status Check
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot pay for cancelled booking",
            )

        if booking.payment_status == PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already paid",
            )

        # 4. Initiate with Gateway (Mock)
        gateway_resp = await payment_service.initiate_transaction(
            amount=booking.total_price,
            currency="INR",  # Default
            description=f"Payment for Booking {booking_id}",
        )

        # 5. Create Payment Record (Pending)
        payment = await payment_crud.create_payment(
            booking_id=booking_id,
            customer_id=customer_id,
            amount=booking.total_price,
            currency="INR",
            method=method,
            transaction_id=gateway_resp["transaction_id"],
        )

        return {
            "payment_id": str(payment.id),
            "booking_id": booking_id,
            "transaction_id": gateway_resp["transaction_id"],
            "amount": booking.total_price,
            "currency": "INR",
            "payment_url": gateway_resp["payment_url"],
            "status": "pending",
        }

    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Manually verify a payment status (Simulated Webhook).
        In real frontend, user would return to success page which calls this.
        """
        # 1. Fetch Payment
        payment = await payment_crud.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")

        if payment.status == TransactionStatus.COMPLETED:
            return {"status": "completed", "message": "Already paid"}

        # 2. Call Gateway Service to Check Status
        # Using mock service verification
        is_success, gateway_status = await payment_service.verify_payment(
            str(payment.transaction_id)
        )

        if is_success:
            # 3. Update Payment Record
            await payment_crud.update_status(
                str(payment.id),
                TransactionStatus.COMPLETED,
                gateway_response={"status": gateway_status},
            )

            # 4. Update Booking Record -> PAID
            booking = await booking_crud.get_booking_by_id(payment.booking_id)
            if booking:
                # If booking was pending, maybe confirm it automatically?
                # For now, just mark paid.
                # Logic: If booking is still PENDING, we mark it CONFIRMED if paid?
                # Or keep it PENDING until cleaner accepts?
                # Let's keep status pending but payment completed.
                # Cleaner accepts -> Confirmed.
                await booking_crud.update_payment_status(
                    str(booking.id), PaymentStatus.COMPLETED
                )

            return {"status": "completed", "booking_id": payment.booking_id}

        else:
            # Mark failed
            await payment_crud.update_status(
                str(payment.id),
                TransactionStatus.FAILED,
                gateway_response={"status": gateway_status},
            )
            return {"status": "failed", "message": "Payment verification failed"}

    async def get_booking_payment_status(self, booking_id: str) -> Dict[str, Any]:
        """Get status of payment for a booking."""
        payment = await payment_crud.get_payment_by_booking(booking_id)
        if not payment:
            return {"status": "not_initiated", "booking_paid": False}

        booking = await booking_crud.get_booking_by_id(booking_id)
        is_paid = (
            booking.payment_status == PaymentStatus.COMPLETED if booking else False
        )

        return {
            "payment_id": str(payment.id),
            "status": payment.status,
            "booking_paid": is_paid,
        }


payment_controller = PaymentController()
