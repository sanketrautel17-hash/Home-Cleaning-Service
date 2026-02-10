"""
Service Controller
==================
Business logic for service package management operations.

Handles:
- Create service package (role + ownership check)
- Get service details
- Update / delete service (ownership check)
- List services by cleaner
- Search services (by category, price range)
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from cruds.service_crud import service_crud
from cruds.cleaner_crud import cleaner_crud
from cruds.user_crud import user_crud
from commons.logger import logger
from models.user_model import User
from models.service_model import ServicePackage

# Initialize logger
log = logger(__name__)


class ServiceController:
    """
    Service package management controller.

    This class contains all service-related business logic,
    including role checks, ownership validation, and search.

    Usage:
        service_controller = ServiceController()
        result = await service_controller.create_service(user, service_data)
    """

    # =========================================================================
    # CREATE SERVICE
    # =========================================================================

    async def create_service(
        self,
        user: User,
        name: str,
        price: float,
        description: Optional[str] = None,
        category: str = "regular",
        price_type: str = "flat",
        duration_hours: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Create a new service package.

        Business rules:
        - Only users with role='cleaner' can create services
        - Cleaner must have a profile first
        - Maximum 20 services per cleaner

        Args:
            user: Current authenticated user (must be a cleaner)
            name: Service display name
            price: Base price amount
            description: Service description
            category: Cleaning category
            price_type: Pricing model
            duration_hours: Estimated duration

        Returns:
            Dictionary with created service data

        Raises:
            HTTPException 403: If user is not a cleaner
            HTTPException 404: If cleaner profile not found
            HTTPException 400: If service limit reached
        """
        log.info(f"Creating service for cleaner: {user.email}")

        # Role check
        if user.role.value != "cleaner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only cleaners can create service packages",
            )

        # Verify cleaner has a profile
        profile = await cleaner_crud.get_profile_by_user_id(str(user.id))
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Create a cleaner profile first before adding services",
            )

        # Build service data
        service_data = {
            "cleaner_id": str(user.id),
            "name": name,
            "description": description,
            "category": category,
            "price": price,
            "price_type": price_type,
            "duration_hours": duration_hours,
        }

        try:
            service = await service_crud.create_service(service_data)
            log.info(f"Service created: '{name}' by {user.email}")

            return {
                "service": self._service_to_dict(service),
                "message": "Service package created successfully",
                "success": True,
            }

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            log.error(f"Service creation error for {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the service",
            )

    # =========================================================================
    # GET SERVICES
    # =========================================================================

    async def get_service(self, service_id: str) -> Dict[str, Any]:
        """
        Get a single service package by ID.

        Args:
            service_id: Service's ObjectId as string

        Returns:
            Dictionary with service data

        Raises:
            HTTPException 404: If service not found
        """
        log.info(f"Getting service: {service_id}")

        service = await service_crud.get_service_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service package not found",
            )

        return {"service": self._service_to_dict(service)}

    async def get_my_services(self, user: User) -> Dict[str, Any]:
        """
        Get all services for the current cleaner.

        Args:
            user: Current authenticated user (must be a cleaner)

        Returns:
            Dictionary with list of services

        Raises:
            HTTPException 403: If user is not a cleaner
        """
        log.info(f"Getting services for cleaner: {user.email}")

        if user.role.value != "cleaner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only cleaners have service packages",
            )

        services = await service_crud.get_services_by_cleaner(str(user.id))

        return {
            "services": [self._service_to_dict(s) for s in services],
            "total": len(services),
        }

    async def get_services_by_cleaner(self, user_id: str) -> Dict[str, Any]:
        """
        Get all active services offered by a specific cleaner (public).

        Args:
            user_id: Cleaner's user ID

        Returns:
            Dictionary with list of active services
        """
        log.info(f"Getting services for cleaner ID: {user_id}")

        # Only return active services to the public
        services = await service_crud.get_services_by_cleaner(user_id, active_only=True)

        return {
            "services": [self._service_to_dict(s) for s in services],
            "total": len(services),
        }

    # =========================================================================
    # UPDATE SERVICE
    # =========================================================================

    async def update_service(
        self,
        user: User,
        service_id: str,
        update_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update a service package.

        Business rules:
        - Only the cleaner who owns the service can update it

        Args:
            user: Current authenticated user
            service_id: Service's ObjectId
            update_data: Fields to update

        Returns:
            Dictionary with updated service data

        Raises:
            HTTPException 403: If user doesn't own the service
            HTTPException 404: If service not found
        """
        log.info(f"Updating service {service_id} by {user.email}")

        # Verify ownership
        service = await service_crud.get_service_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service package not found",
            )

        if service.cleaner_id != str(user.id):
            log.warning(
                f"Unauthorized service update attempt: {user.email} "
                f"tried to update service owned by {service.cleaner_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own services",
            )

        # Filter out None values
        clean_data = {k: v for k, v in update_data.items() if v is not None}

        if not clean_data:
            return {
                "service": self._service_to_dict(service),
                "message": "No changes made",
            }

        try:
            updated = await service_crud.update_service(service_id, clean_data)

            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update service",
                )

            log.info(f"Service {service_id} updated by {user.email}")

            return {
                "service": self._service_to_dict(updated),
                "message": "Service updated successfully",
                "success": True,
            }

        except Exception as e:
            log.error(f"Service update error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the service",
            )

    # =========================================================================
    # DELETE SERVICE
    # =========================================================================

    async def delete_service(self, user: User, service_id: str) -> Dict[str, Any]:
        """
        Delete a service package.

        Business rules:
        - Only the cleaner who owns the service can delete it

        Args:
            user: Current authenticated user
            service_id: Service's ObjectId

        Returns:
            Dictionary with success message

        Raises:
            HTTPException 403: If user doesn't own the service
            HTTPException 404: If service not found
        """
        log.info(f"Deleting service {service_id} by {user.email}")

        # Verify ownership
        service = await service_crud.get_service_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service package not found",
            )

        if service.cleaner_id != str(user.id):
            log.warning(
                f"Unauthorized service delete attempt: {user.email} "
                f"tried to delete service owned by {service.cleaner_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own services",
            )

        success = await service_crud.delete_service(service_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete service",
            )

        log.info(f"Service {service_id} deleted by {user.email}")

        return {"message": "Service deleted successfully", "success": True}

    # =========================================================================
    # SEARCH SERVICES
    # =========================================================================

    async def search_services(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        price_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "price_low",
    ) -> Dict[str, Any]:
        """
        Search service packages with filters and pagination.

        Args:
            category: Filter by service category
            min_price: Minimum price
            max_price: Maximum price
            price_type: Filter by pricing model
            skip: Pagination offset
            limit: Max results (capped at 50)
            sort_by: Sort order

        Returns:
            Dictionary with service list and pagination
        """
        log.info(
            f"Searching services: category={category}, price={min_price}-{max_price}"
        )

        # Cap limit
        limit = min(limit, 50)

        services = await service_crud.search_services(
            category=category,
            min_price=min_price,
            max_price=max_price,
            price_type=price_type,
            active_only=True,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
        )

        total = await service_crud.count_services(
            category=category,
            min_price=min_price,
            max_price=max_price,
            price_type=price_type,
            active_only=True,
        )

        # Enrich with cleaner info
        enriched = []
        for service in services:
            enriched.append(await self._service_with_cleaner(service))

        return {
            "services": enriched,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + len(services) < total,
            },
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _service_to_dict(self, service: ServicePackage) -> Dict[str, Any]:
        """
        Convert ServicePackage to dictionary.
        """
        return {
            "id": str(service.id),
            "cleaner_id": service.cleaner_id,
            "name": service.name,
            "description": service.description,
            "category": service.category.value,
            "price": service.price,
            "price_type": service.price_type.value,
            "duration_hours": service.duration_hours,
            "is_active": service.is_active,
            "created_at": (
                service.created_at.isoformat() if service.created_at else None
            ),
            "updated_at": (
                service.updated_at.isoformat() if service.updated_at else None
            ),
        }

    async def _service_with_cleaner(self, service: ServicePackage) -> Dict[str, Any]:
        """
        Convert ServicePackage to dictionary with cleaner info attached.
        Used in search results so customers know who offers the service.
        """
        data = self._service_to_dict(service)

        # Add cleaner info
        user = await user_crud.get_user_by_id(service.cleaner_id)
        profile = await cleaner_crud.get_profile_by_user_id(service.cleaner_id)

        data["cleaner_name"] = user.full_name if user else None
        data["cleaner_rating"] = profile.avg_rating if profile else 0.0
        data["cleaner_city"] = profile.city if profile else None

        return data


# Create singleton instance for easy import
service_controller = ServiceController()
