# Request Schemas Package
# Contains Pydantic models for API request validation

from core.apis.schemas.requests.auth_request import (
    UserRegisterRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from core.apis.schemas.requests.user_request import (
    UpdateProfileRequest,
    DeleteAccountRequest,
)
from core.apis.schemas.requests.cleaner_request import (
    CreateCleanerProfileRequest,
    UpdateCleanerProfileRequest,
)
from core.apis.schemas.requests.service_request import (
    CreateServiceRequest,
    UpdateServiceRequest,
)

__all__ = [
    # Auth
    "UserRegisterRequest",
    "UserLoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    # User
    "UpdateProfileRequest",
    "DeleteAccountRequest",
    # Cleaner
    "CreateCleanerProfileRequest",
    "UpdateCleanerProfileRequest",
    # Service
    "CreateServiceRequest",
    "UpdateServiceRequest",
]
