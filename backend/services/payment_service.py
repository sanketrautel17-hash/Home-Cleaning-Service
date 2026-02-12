"""
Mock Payment Service
====================
Simulates interactions with an external payment gateway (e.g., Stripe, Razorpay).

In a real world scenario, this would use the gateway's SDK or API.
For MVP, we generate fake transaction IDs and simulate success/failure.
"""

import uuid
import random
from typing import Dict, Any, Tuple


class PaymentService:
    """
    Mock service to handle payment processing logic.
    """

    async def initiate_transaction(
        self, amount: float, currency: str = "INR", description: str = "Service Booking"
    ) -> Dict[str, Any]:
        """
        Start a payment intent.

        Returns:
            Dict containing 'transaction_id' and 'gateway_url' (mock).
        """
        # Generate a fake transaction ID (like 'pay_L8S9dcc83jD')
        txn_id = f"pay_{uuid.uuid4().hex[:12]}"

        # In a real app, this would call Stripe.PaymentIntent.create()
        return {
            "transaction_id": txn_id,
            "status": "created",
            "amount": amount,
            "currency": currency,
            # Mock URL where frontend would redirect user
            "payment_url": f"https://mock-gateway.com/pay/{txn_id}",
        }

    async def verify_payment(self, transaction_id: str) -> Tuple[bool, str]:
        """
        Verify if a transaction was successful.

        For simulation:
        - We assume all valid IDs succeed
        - We could add random failure logic here if desired
        """
        if not transaction_id.startswith("pay_"):
            return False, "failed"

        # Simulate check
        return True, "captured"

    def generate_receipt_id(self) -> str:
        """Generate a receipt number."""
        return f"RCPT-{uuid.uuid4().hex[:8].upper()}"


payment_service = PaymentService()
