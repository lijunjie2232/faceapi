"""
Admin routes module for the Face Recognition System.

This module defines the administrative API endpoints for managing users,
including listing, creating, updating, and deleting user accounts.
"""

import logging
from traceback import print_exc
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from tortoise.transactions import atomic

from ..schemas import (
    DataResponse,
    ListResponse,
    User,
    UserCreateAsAdmin,
    UserUpdateAsAdmin,
    BatchOperationRequest,
    BatchOperationResult,
)
from ..services import (
    create_user_as_admin_service,
    get_user_service,
    list_users_service,
    update_user_as_admin_service,
    validate_user_update_uniqueness,
    update_face_embedding_service,
    batch_reset_password_service,
    batch_activate_users_service,
    batch_deactivate_users_service,
    batch_reset_face_data_service,
)
from ..models import UserModel
from ..utils import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)
logger = logging.getLogger(__name__)


@router.get(
    "/users",
    response_model=ListResponse[User],
    dependencies=[Depends(get_current_admin_user)],
)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
):
    """Admin endpoint to list all users with pagination"""
    try:
        limit = min(100, max(limit, 1))
        users, count = await list_users_service(skip, limit)

        return ListResponse[User](
            success=True,
            message="Users retrieved successfully",
            data=users,
            total=count,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing users: {str(e)}",
        ) from e


@router.get(
    "/users/{user_id}",
    response_model=DataResponse[User],
    dependencies=[Depends(get_current_admin_user)],
)
async def get_user_by_id(
    user_id: int,
):
    """Admin endpoint to get a specific user by ID"""
    try:
        user = await get_user_service(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_response = User(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            head_pic=user.head_pic,
            is_admin=user.is_admin,
        )

        return DataResponse[User](
            success=True,
            message="User retrieved successfully",
            data=user_response,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}",
        ) from e


@router.post(
    "/users",
    response_model=DataResponse[User],
    dependencies=[Depends(get_current_admin_user)],
)
async def create_user_as_admin(
    user_create: UserCreateAsAdmin,
):
    """Admin endpoint to create a new user"""
    try:
        # Check if user already exists
        existing_user = await get_user_service(username=user_create.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken",
            )

        existing_email = await get_user_service(email=user_create.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        # Create the user via service
        created_user = await create_user_as_admin_service(user_create)

        # Convert to response format
        user_response = User(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
            head_pic=created_user.head_pic,
            is_admin=created_user.is_admin,
        )

        return DataResponse[User](
            success=True,
            message="User created successfully",
            data=user_response,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400 if "already" in str(e) or "duplicate" in str(e) else 500,
            detail=f"Error creating user: {str(e)}",
        ) from e


@router.put(
    "/users/{user_id}",
    response_model=DataResponse[User],
    dependencies=[Depends(get_current_admin_user)],
)
async def update_user_as_admin(
    user_id: int,
    user_update: UserUpdateAsAdmin,
    current_admin: UserModel = Depends(get_current_admin_user),
):
    """Admin endpoint to update a specific user by ID"""
    try:
        # Get the user to check if it exists
        user = await get_user_service(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_id == current_admin.id:
            # even though the current user is admin, self-active/inactive is not allowed
            if user_update.is_active is not None:
                raise HTTPException(status_code=400, detail="Cannot change own status")

        # Validate uniqueness of username and email
        validation_error = await validate_user_update_uniqueness(user_id, user_update)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)

        # Update the user via service
        updated_user = await update_user_as_admin_service(user_id, user_update)

        user_response = User(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            head_pic=updated_user.head_pic,
            is_admin=updated_user.is_admin,
        )

        return DataResponse[User](
            success=True, message="User updated successfully", data=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400 if "already" in str(e) or "duplicate" in str(e) else 500,
            detail=f"Error updating user: {str(e)}",
        ) from e


@atomic()
@router.post(
    "/batch/{operation}",
    response_model=DataResponse[BatchOperationResult],
    dependencies=[Depends(get_current_admin_user)],
)
async def batch_operation(
    operation: str,
    batch_request: BatchOperationRequest,
    current_admin: UserModel = Depends(get_current_admin_user),
):
    """
    Admin endpoint to perform batch operations on multiple users.

    Supported operations:
    - reset-password: Reset passwords to specified value
    - active: Activate user accounts
    - inactive: Deactivate user accounts
    - reset-face: Reset face data to unset

    Args:
        operation: The operation to perform
        batch_request: Request containing user_ids and optional value
        current_admin: Current admin user (dependency)

    Returns:
        BatchOperationResult with success/failure statistics
    """
    # Validate operation
    valid_operations = ["reset-password", "active", "inactive", "reset-face"]
    if operation not in valid_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation. Valid operations are: {valid_operations}",
        )

    # Validate user_ids
    if not batch_request.user_ids:
        raise HTTPException(status_code=400, detail="user_ids list cannot be empty")

    # Check for self-operation restrictions
    if current_admin.id in batch_request.user_ids:
        raise HTTPException(
            status_code=400, detail="Cannot inclued your own account in batch operation"
        )

    # Validate value requirement
    if operation == "reset-password" and not batch_request.value:
        raise HTTPException(
            status_code=400, detail="Value is required for reset-password operation"
        )

    try:
        # Perform the requested operation
        if operation == "reset-password":
            result = await batch_reset_password_service(
                batch_request.user_ids, batch_request.value
            )
        elif operation == "active":
            result = await batch_activate_users_service(batch_request.user_ids)
        elif operation == "inactive":
            result = await batch_deactivate_users_service(batch_request.user_ids)
        elif operation == "reset-face":
            result = await batch_reset_face_data_service(batch_request.user_ids)
        else:
            # This shouldn't happen due to validation above, but added for completeness
            raise HTTPException(status_code=500, detail="Unsupported operation")

        return DataResponse[BatchOperationResult](
            success=True, message=f"Batch {operation} operation completed", data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing batch operation: {str(e)}",
        ) from e


# update the face of any user as admin
@atomic()
@router.put(
    "/face/{user_id}",
    dependencies=[Depends(get_current_admin_user)],
)
async def update_face_embedding_as_admin(
    user_id: int,
    image: UploadFile = File(...),
):
    """
    Update the face embedding for the specified user as an admin.
    This endpoint allows an admin to update the face embedding for a specific user.
    It uses the existing face embedding service but adds admin-level validation and error handling.

    Args:
        user_id (int): The ID of the user whose face embedding to update
        image (UploadFile): The uploaded image containing the user's face

    Returns:
        Success message indicating the embedding was updated
    """
    try:
        result = await update_face_embedding_service(user_id, image)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print_exc()
        logger.error("Error in face embedding update: %s", str(e))
        raise e
