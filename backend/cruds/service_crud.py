"""
Service CRUD Operations
=======================
Database operations for ServicePackage model using ODMantic.
Handles all service package-related database queries and mutations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from odmantic import AIOEngine

from models.service_model import ServicePackage, PriceType
from models.cleaner_profile_model import ServiceCategory
from database.database import get_engine


class ServiceCRUD:
    """
    CRUD operations for ServicePackage model.

    All methods are async and use ODMantic engine for MongoDB operations.

    Usage:
        service_crud = ServiceCRUD()
        service = await service_crud.create_service({
            "cleaner_id": "...", "name": "Deep Cleaning", "price": 1500.0
        })
    """

    # Maximum number of services a single cleaner can create
    MAX_SERVICES_PER_CLEANER = 20

    def __init__(self, engine: Optional[AIOEngine] = None):
        """
        Initialize ServiceCRUD with optional custom engine.

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

    async def create_service(self, service_data: Dict[str, Any]) -> ServicePackage:
        """
        Create a new service package.

        Args:
            service_data: Dictionary containing service fields:
                - cleaner_id (required): Reference to the cleaner User
                - name (required): Service display name
                - price (required): Base price amount
                - description, category, price_type, duration_hours

        Returns:
            Created ServicePackage object

        Raises:
            ValueError: If cleaner has reached maximum services limit

        Example:
            >>> service = await service_crud.create_service({
            ...     "cleaner_id": "507f1f77bcf86cd799439012",
            ...     "name": "Premium Deep Cleaning",
            ...     "price": 1500.0,
            ...     "category": "deep",
            ...     "price_type": "flat",
            ...     "duration_hours": 3.0,
            ... })
        """
        cleaner_id = service_data["cleaner_id"]

        # Check service count limit
        current_count = await self.count_services_by_cleaner(cleaner_id)
        if current_count >= self.MAX_SERVICES_PER_CLEANER:
            raise ValueError(
                f"Maximum {self.MAX_SERVICES_PER_CLEANER} services per cleaner reached"
            )

        # Convert category string to enum
        category = ServiceCategory(service_data.get("category", "regular").lower())

        # Convert price_type string to enum
        price_type = PriceType(service_data.get("price_type", "flat").lower())

        # Create service object
        service = ServicePackage(
            cleaner_id=cleaner_id,
            name=service_data["name"].strip(),
            description=service_data.get("description"),
            category=category,
            price=service_data["price"],
            price_type=price_type,
            duration_hours=service_data.get("duration_hours", 1.0),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        await self.engine.save(service)
        return service

    # =========================================================================
    # READ Operations
    # =========================================================================

    async def get_service_by_id(self, service_id: str) -> Optional[ServicePackage]:
        """
        Get a service package by its ID.

        Args:
            service_id: Service's ObjectId as string

        Returns:
            ServicePackage if found, None otherwise
        """
        try:
            return await self.engine.find_one(
                ServicePackage, ServicePackage.id == ObjectId(service_id)
            )
        except Exception:
            return None

    async def get_services_by_cleaner(
        self,
        cleaner_id: str,
        active_only: bool = False,
    ) -> List[ServicePackage]:
        """
        Get all service packages offered by a cleaner.

        Args:
            cleaner_id: Cleaner's User ID as string
            active_only: If True, only return active services

        Returns:
            List of ServicePackage objects
        """
        filters = [ServicePackage.cleaner_id == cleaner_id]

        if active_only:
            filters.append(ServicePackage.is_active == True)

        services = await self.engine.find(ServicePackage, *filters)
        return list(services)

    async def count_services_by_cleaner(self, cleaner_id: str) -> int:
        """
        Count total services for a cleaner.

        Args:
            cleaner_id: Cleaner's User ID as string

        Returns:
            Count of services
        """
        return await self.engine.count(
            ServicePackage, ServicePackage.cleaner_id == cleaner_id
        )

    async def search_services(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        price_type: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "price_low",
    ) -> List[ServicePackage]:
        """
        Search service packages with filters.

        Args:
            category: Filter by service category
            min_price: Minimum price
            max_price: Maximum price
            price_type: Filter by pricing model
            active_only: Only return active services
            skip: Pagination offset
            limit: Maximum results
            sort_by: Sort - 'price_low', 'price_high', 'newest', 'duration'

        Returns:
            List of matching ServicePackage objects
        """
        filters = []

        if category:
            filters.append(ServicePackage.category == ServiceCategory(category.lower()))

        if min_price is not None:
            filters.append(ServicePackage.price >= min_price)

        if max_price is not None:
            filters.append(ServicePackage.price <= max_price)

        if price_type:
            filters.append(ServicePackage.price_type == PriceType(price_type.lower()))

        if active_only:
            filters.append(ServicePackage.is_active == True)

        # Execute query
        if filters:
            services = await self.engine.find(
                ServicePackage, *filters, skip=skip, limit=limit
            )
        else:
            services = await self.engine.find(ServicePackage, skip=skip, limit=limit)

        # Sort results
        result = list(services)
        if sort_by == "price_low":
            result.sort(key=lambda s: s.price)
        elif sort_by == "price_high":
            result.sort(key=lambda s: s.price, reverse=True)
        elif sort_by == "newest":
            result.sort(key=lambda s: s.created_at, reverse=True)
        elif sort_by == "duration":
            result.sort(key=lambda s: s.duration_hours)

        return result

    async def count_services(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        price_type: Optional[str] = None,
        active_only: bool = True,
    ) -> int:
        """
        Count services matching filters.

        Args:
            Same filters as search_services()

        Returns:
            Total count of matching services
        """
        filters = []

        if category:
            filters.append(ServicePackage.category == ServiceCategory(category.lower()))

        if min_price is not None:
            filters.append(ServicePackage.price >= min_price)

        if max_price is not None:
            filters.append(ServicePackage.price <= max_price)

        if price_type:
            filters.append(ServicePackage.price_type == PriceType(price_type.lower()))

        if active_only:
            filters.append(ServicePackage.is_active == True)

        if filters:
            return await self.engine.count(ServicePackage, *filters)
        else:
            return await self.engine.count(ServicePackage)

    # =========================================================================
    # UPDATE Operations
    # =========================================================================

    async def update_service(
        self, service_id: str, update_data: Dict[str, Any]
    ) -> Optional[ServicePackage]:
        """
        Update service package fields.

        Args:
            service_id: Service's ObjectId as string
            update_data: Dictionary of fields to update

        Returns:
            Updated ServicePackage if found, None otherwise

        Example:
            >>> service = await service_crud.update_service(
            ...     service_id="507f1f77bcf86cd799439013",
            ...     update_data={"price": 2000.0, "name": "Updated Name"}
            ... )
        """
        service = await self.get_service_by_id(service_id)
        if not service:
            return None

        # Direct fields that can be updated
        allowed_fields = {
            "name",
            "description",
            "price",
            "duration_hours",
            "is_active",
        }

        for field, value in update_data.items():
            if field in allowed_fields and value is not None:
                setattr(service, field, value)

        # Handle category separately (needs enum conversion)
        if "category" in update_data and update_data["category"] is not None:
            service.category = ServiceCategory(update_data["category"].lower())

        # Handle price_type separately (needs enum conversion)
        if "price_type" in update_data and update_data["price_type"] is not None:
            service.price_type = PriceType(update_data["price_type"].lower())

        # Update timestamp
        service.update_timestamp()

        # Save changes
        await self.engine.save(service)
        return service

    async def toggle_service_active(
        self, service_id: str, is_active: bool
    ) -> Optional[ServicePackage]:
        """
        Activate or deactivate a service package.

        Args:
            service_id: Service's ObjectId as string
            is_active: New active status

        Returns:
            Updated ServicePackage if found, None otherwise
        """
        service = await self.get_service_by_id(service_id)
        if not service:
            return None

        service.is_active = is_active
        service.update_timestamp()

        await self.engine.save(service)
        return service

    # =========================================================================
    # DELETE Operations
    # =========================================================================

    async def delete_service(self, service_id: str) -> bool:
        """
        Permanently delete a service package.

        Args:
            service_id: Service's ObjectId as string

        Returns:
            True if deleted successfully, False if not found
        """
        service = await self.get_service_by_id(service_id)
        if not service:
            return False

        await self.engine.delete(service)
        return True

    async def delete_all_services_by_cleaner(self, cleaner_id: str) -> int:
        """
        Delete ALL services for a cleaner (used when deleting cleaner profile).

        Args:
            cleaner_id: Cleaner's User ID as string

        Returns:
            Number of services deleted
        """
        services = await self.get_services_by_cleaner(cleaner_id)
        count = 0
        for service in services:
            await self.engine.delete(service)
            count += 1
        return count


# Create a singleton instance for easy import
service_crud = ServiceCRUD()
