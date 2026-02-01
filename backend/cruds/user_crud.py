"""
User CRUD Operations
====================
Database operations for User model using ODMantic.
Handles all user-related database queries and mutations.
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from odmantic import AIOEngine

from models.user_model import User, UserRole
from commons.security import hash_password, verify_password
from database.database import get_engine


class UserCRUD:
    """
    CRUD operations for User model.

    All methods are async and use ODMantic engine for MongoDB operations.

    Usage:
        user_crud = UserCRUD()
        user = await user_crud.create_user(email="...", password="...", ...)
    """

    def __init__(self, engine: Optional[AIOEngine] = None):
        """
        Initialize UserCRUD with optional custom engine.

        Args:
            engine: Optional ODMantic engine. If not provided, uses default.
        """
        self._engine = engine

    @property
    def engine(self) -> AIOEngine:
        """Get the ODMantic engine."""
        return self._engine or get_engine()

    # =========================================================================
    # CREATE Operations
    # =========================================================================

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "customer",
        phone: Optional[str] = None,
    ) -> User:
        """
        Create a new user with hashed password.

        Args:
            email: User's email address (must be unique)
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role - 'customer' or 'cleaner'
            phone: Optional phone number

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists

        Example:
            >>> user = await user_crud.create_user(
            ...     email="user@example.com",
            ...     password="SecurePass123!",
            ...     full_name="John Doe",
            ...     role="customer"
            ... )
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Hash the password
        password_hash = hash_password(password)

        # Convert role string to enum
        user_role = UserRole.CUSTOMER if role == "customer" else UserRole.CLEANER

        # Create user object
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role=user_role,
            phone=phone,
            is_active=True,
            email_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        await self.engine.save(user)
        return user

    async def create_google_user(
        self,
        email: str,
        full_name: str,
        google_id: str,
        profile_pic: Optional[str] = None,
        role: str = "customer",
    ) -> User:
        """
        Create a new user from Google OAuth.

        Args:
            email: User's email from Google
            full_name: User's full name from Google
            google_id: Google's unique user ID
            profile_pic: Profile picture URL from Google
            role: User role - 'customer' or 'cleaner'

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists

        Example:
            >>> user = await user_crud.create_google_user(
            ...     email="user@gmail.com",
            ...     full_name="John Doe",
            ...     google_id="123456789",
            ...     profile_pic="https://..."
            ... )
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Convert role string to enum
        user_role = UserRole.CUSTOMER if role == "customer" else UserRole.CLEANER

        # Create user object (no password for OAuth users)
        user = User(
            email=email.lower().strip(),
            password_hash=None,  # No password for OAuth users
            auth_provider="google",
            google_id=google_id,
            full_name=full_name.strip() if full_name else None,
            profile_pic=profile_pic,
            role=user_role,
            is_active=True,
            email_verified=True,  # Google already verified the email
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        await self.engine.save(user)
        return user

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """
        Get a user by their Google ID.

        Args:
            google_id: Google's unique user ID

        Returns:
            User object if found, None otherwise
        """
        return await self.engine.find_one(User, User.google_id == google_id)

    async def update_user_google_info(
        self,
        user_id: str,
        google_id: str,
        profile_pic: Optional[str] = None,
    ) -> Optional[User]:
        """
        Link an existing user account with Google OAuth.

        Args:
            user_id: User's ObjectId as string
            google_id: Google's unique user ID
            profile_pic: Optional profile picture URL from Google

        Returns:
            Updated User object if found, None otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.auth_provider = "google"
        user.google_id = google_id
        user.email_verified = True  # Google verified the email

        if profile_pic and not user.profile_pic:
            user.profile_pic = profile_pic

        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return user

    # =========================================================================
    # READ Operations
    # =========================================================================

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: User's ObjectId as string

        Returns:
            User object if found, None otherwise
        """
        try:
            user = await self.engine.find_one(User, User.id == ObjectId(user_id))
            return user
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        return await self.engine.find_one(User, User.email == email.lower().strip())

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """
        Get all users with optional filtering and pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            role: Optional role filter ('customer' or 'cleaner')
            is_active: Optional active status filter

        Returns:
            List of User objects
        """
        # Build query filters
        filters = []

        if role:
            user_role = UserRole.CUSTOMER if role == "customer" else UserRole.CLEANER
            filters.append(User.role == user_role)

        if is_active is not None:
            filters.append(User.is_active == is_active)

        # Execute query
        if filters:
            users = await self.engine.find(User, *filters, skip=skip, limit=limit)
        else:
            users = await self.engine.find(User, skip=skip, limit=limit)

        return list(users)

    async def count_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """
        Count total users with optional filtering.

        Args:
            role: Optional role filter
            is_active: Optional active status filter

        Returns:
            Total count of matching users
        """
        filters = []

        if role:
            user_role = UserRole.CUSTOMER if role == "customer" else UserRole.CLEANER
            filters.append(User.role == user_role)

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if filters:
            count = await self.engine.count(User, *filters)
        else:
            count = await self.engine.count(User)

        return count

    # =========================================================================
    # UPDATE Operations
    # =========================================================================

    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user fields.

        Args:
            user_id: User's ObjectId as string
            **kwargs: Fields to update (full_name, phone, profile_pic, etc.)

        Returns:
            Updated User object if found, None otherwise

        Example:
            >>> user = await user_crud.update_user(
            ...     user_id="507f1f77bcf86cd799439011",
            ...     full_name="Jane Doe",
            ...     phone="+919876543210"
            ... )
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = {
            "full_name",
            "phone",
            "profile_pic",
            "is_active",
            "email_verified",
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        # Update timestamp
        user.updated_at = datetime.utcnow()

        # Save changes
        await self.engine.save(user)
        return user

    async def update_password(
        self,
        user_id: str,
        new_password: str,
    ) -> bool:
        """
        Update user's password.

        Args:
            user_id: User's ObjectId as string
            new_password: New plain text password (will be hashed)

        Returns:
            True if updated successfully, False if user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return True

    async def update_password_by_email(
        self,
        email: str,
        new_password: str,
    ) -> bool:
        """
        Update user's password by email.

        Args:
            email: User's email address
            new_password: New plain text password (will be hashed)

        Returns:
            True if updated successfully, False if user not found
        """
        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return True

    async def verify_user_email(self, email: str) -> bool:
        """
        Mark user's email as verified.

        Args:
            email: User's email address

        Returns:
            True if updated successfully, False if user not found
        """
        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.email_verified = True
        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User's ObjectId as string

        Returns:
            True if deactivated successfully, False if user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return True

    async def activate_user(self, user_id: str) -> bool:
        """
        Activate a user account.

        Args:
            user_id: User's ObjectId as string

        Returns:
            True if activated successfully, False if user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()

        await self.engine.save(user)
        return True

    # =========================================================================
    # DELETE Operations
    # =========================================================================

    async def delete_user(self, user_id: str) -> bool:
        """
        Permanently delete a user from the database.

        Args:
            user_id: User's ObjectId as string

        Returns:
            True if deleted successfully, False if user not found

        Note:
            Consider using deactivate_user() for soft delete instead.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.engine.delete(user)
        return True

    # =========================================================================
    # Authentication Helpers
    # =========================================================================

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email address
            password: Plain text password to verify

        Returns:
            User object if authentication successful, None otherwise

        Example:
            >>> user = await user_crud.authenticate_user(
            ...     email="user@example.com",
            ...     password="SecurePass123!"
            ... )
            >>> if user:
            ...     print("Login successful!")
        """
        user = await self.get_user_by_email(email)

        if not user:
            return None

        # Check if user has a password (OAuth users don't have passwords)
        if not user.password_hash:
            return None

        # Check if user is using local auth (not OAuth)
        if user.auth_provider != "local":
            return None

        if not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    async def verify_current_password(
        self,
        user_id: str,
        current_password: str,
    ) -> bool:
        """
        Verify user's current password.

        Args:
            user_id: User's ObjectId as string
            current_password: Current password to verify

        Returns:
            True if password matches, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        return verify_password(current_password, user.password_hash)


# Create a singleton instance for easy import
user_crud = UserCRUD()
