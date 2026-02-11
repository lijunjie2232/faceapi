"""Init module for schemas package.

This module imports and exposes commonly used schemas throughout the application.
"""

from .face import (
    FaceRecognitionRequest,
    FaceRecognitionResponse,
    FaceRecognitionResult,
    FaceRegisterRequest,
)
from .response import DataResponse, ListResponse
from .user import (
    BatchOperationRequest,
    BatchOperationResult,
    User,
    UserBase,
    UserCreate,
    UserCreateAsAdmin,
    UserCreatePydantic,
    UserPydantic,
    UserUpdate,
    UserUpdateAsAdmin,
    UserUpdatePydantic,
)

__all__ = [
    "DataResponse",
    "ListResponse",
    "UserBase",
    "UserCreate",
    "UserCreateAsAdmin",
    "UserCreatePydantic",
    "UserPydantic",
    "UserUpdate",
    "UserUpdateAsAdmin",
    "UserUpdatePydantic",
    "BatchOperationRequest",
    "BatchOperationResult",
    "User",
    "FaceRegisterRequest",
    "FaceRecognitionResult",
]
