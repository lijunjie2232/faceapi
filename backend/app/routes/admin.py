"""
Admin routes module for the Face Recognition System.

This module defines the administrative API endpoints for managing users,
including listing, creating, updating, and deleting user accounts.
"""

from fastapi import APIRouter, Depends, HTTPException

from ..schemas import (
    DataResponse,
    ListResponse,
    User,
    UserCreateAsAdmin,
    UserUpdateAsAdmin,
)
from ..services import (
    activate_user_service,
    create_user_as_admin_service,
    deactivate_user_service,
    get_user_service,
    list_users_service,
    update_user_as_admin_service,
    validate_user_update_uniqueness,
)
from ..utils import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


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
):
    """Admin endpoint to update a specific user by ID"""
    try:
        # Get the user to check if it exists
        user = await get_user_service(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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


@router.delete(
    "/users/{user_id}",
    response_model=DataResponse[bool],
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_user_as_admin(
    user_id: int,
):
    """Admin endpoint to delete a specific user by ID (soft delete)"""
    try:
        # Get the user to check if it exists
        user = await get_user_service(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Perform soft delete by deactivating the user via service
        success = await deactivate_user_service(user_id)

        return DataResponse[bool](
            success=True, message="User deactivated successfully", data=success
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deactivating user: {str(e)}",
        ) from e


@router.patch(
    "/users/{user_id}/activate",
    response_model=DataResponse[bool],
    dependencies=[Depends(get_current_admin_user)],
)
async def activate_user(
    user_id: int,
):
    """Admin endpoint to activate a specific user by ID"""
    try:
        # Get the user to check if it exists
        user = await get_user_service(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Activate the user via service
        success = await activate_user_service(user_id)

        return DataResponse[bool](
            success=True, message="User activated successfully", data=success
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error activating user: {str(e)}",
        ) from e
