"""
Verify User Script
==================
Manually verify a user's email for testing purposes.

Usage:
    python -m scripts.verify_user <email>
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import connect_to_mongo, close_mongo_connection
from cruds.user_crud import user_crud


async def verify_user(email: str):
    """Mark user as verified."""
    await connect_to_mongo()

    print(f"Verifying user: {email}")
    success = await user_crud.verify_user_email(email)

    if success:
        print(f"Successfully verified {email}")
    else:
        print(f"User not found: {email}")
        sys.exit(1)

    await close_mongo_connection()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.verify_user <email>")
        sys.exit(1)

    email = sys.argv[1]
    asyncio.run(verify_user(email))
