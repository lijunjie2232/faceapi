"""
Services module for the Face Recognition System.

This module contains business logic implementations for various
functionalities of the application, separated from the API route handlers.
"""

from .admin import (
    activate_user_service,
    create_user_as_admin_service,
    deactivate_user_service,
    list_users_service,
    update_user_as_admin_service,
    validate_user_update_uniqueness,
    batch_reset_password_service,
    batch_activate_users_service,
    batch_deactivate_users_service,
    batch_reset_face_data_service,
)
from .face import update_face_embedding_service, verify_face_service
from .user import (
    create_user_service,
    delete_user_account_service,
    get_current_user_profile_service,
    get_user_service,
)

__ALL__ = [
    "list_users_service",
    "update_user_as_admin_service",
    "create_user_as_admin_service",
    "deactivate_user_service",
    "activate_user_service",
    "validate_user_update_uniqueness",
    "update_face_embedding_service",
    "verify_face_service",
    "update_user_profile_service",
    "create_user_service",
    "delete_user_account_service",
    "get_current_user_profile_service",
    "get_user_service",
    "batch_reset_password_service",
    "batch_activate_users_service",
    "batch_deactivate_users_service",
    "batch_reset_face_data_service",
]
