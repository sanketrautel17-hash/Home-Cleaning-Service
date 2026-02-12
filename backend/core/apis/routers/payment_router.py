"""
Payment Router
==============
FastAPI routes for payment processing.
Prefix: /api/payments
"""

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Dict, Any

from controllers.payment_controller import payment_controller
from commons.dependencies import require_customer, get_current_user
from models.user_model import User
from core.apis.schemas.requests.payment_request import InitiatePaymentRequest
from core.apis.schemas.responses.payment_response import PaymentStatusResponse

router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


@router.post(
    "/initiate",
    status_code=status.HTTP_201_CREATED,
    summary="Initiate a payment",
    description="Start payment process for a booking.",
)
async def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(require_customer),
):
    """
    Start payment session.
    Only the customer who made the booking can pay.
    """
    return await payment_controller.initiate_payment(
        customer_id=str(current_user.id),
        booking_id=request.booking_id,
        method=request.method,
    )


@router.post(
    "/verify/{payment_id}",
    status_code=status.HTTP_200_OK,
    summary="Verify payment status",
    description="Check payment status and confirm booking as paid if successful.",
)
async def verify_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Verify payment completion.
    """
    # Anyone authenticated can verify (technically frontend callback)
    # But usually restricted to relevant user or system
    return await payment_controller.verify_payment(payment_id)


@router.get(
    "/status/{booking_id}",
    response_model=PaymentStatusResponse,
    summary="Get payment status",
    description="Check if a booking is paid.",
)
async def get_payment_status(
    booking_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Check payment status for a booking.
    """
    result = await payment_controller.get_booking_payment_status(booking_id)
    return {
        "booking_paid": result.get("booking_paid", False),
        "status": str(result.get("status", "unknown")),
        "payment_id": str(result.get("payment_id", "")),
    }
