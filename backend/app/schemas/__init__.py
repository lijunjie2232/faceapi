"""Init module for schemas package.

This module imports and exposes commonly used schemas throughout the application.
"""

from .response import DataResponse, ListResponse
from .user import (
    User,
    UserCreate,
    UserCreateAsAdmin,
    UserInDB,
    UserUpdate,
    UserUpdateAsAdmin,
    UserUpdatePydantic,
)

__ALL__ = [
    "User",
    "UserCreate",
    "UserInDB",
    "UserUpdate",
    "DataResponse",
    "ListResponse",
    "UserUpdatePydantic",
    "UserUpdateAsAdmin",
    "UserCreateAsAdmin",
]
