"""
User Model
==========
Database document model for user accounts in the Home Cleaning Service platform.
Supports both Customer and Cleaner roles with core authentication fields.

Technology: ODMantic (MongoDB ODM for FastAPI)
Collection: users
"""

from odmantic import Model, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """
    User role enumeration for role-based access control.
    - CUSTOMER: Can book cleaning services
    - CLEANER: Can offer cleaning services and accept bookings
    """

    CUSTOMER = "customer"
    CLEANER = "cleaner"


class User(Model):
    """
    User document model representing platform user accounts.

    This model stores core authentication and profile information.
    Cleaners will have an extended profile in a separate CleanerProfile model.

    Attributes:
        email: Unique email address for login (indexed)
        password_hash: Bcrypt hashed password (never store plain text)
        role: User type - customer or cleaner
        phone: Contact phone number
        full_name: User's full name
        profile_pic: URL to profile image
        is_active: Account status (for suspensions)
        email_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
    """

    # Core Authentication Fields
    email: str = Field(unique=True, index=True)
    password_hash: Optional[str] = None  # Optional for OAuth users

    # OAuth Fields
    auth_provider: str = Field(default="local")  # "local" or "google"
    google_id: Optional[str] = None  # Google's unique user ID

    # Role & Profile
    role: UserRole = Field(default=UserRole.CUSTOMER, index=True)
    phone: Optional[str] = None
    full_name: Optional[str] = None
    profile_pic: Optional[str] = None

    # Account Status
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "users"}

    def update_timestamp(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"User(email={self.email}, role={self.role.value})"
