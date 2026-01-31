"""
User routes module for the Face Recognition System.

This module defines the API endpoints for user management,
including authentication, profile management, and account operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import DataResponse, User, UserCreate, UserUpdate
from ..services.user import (
    authenticate_user,
    create_user_service,
    delete_user_account_service,
    get_current_user_profile_service,
    update_user_profile_service,
)
from ..utils import create_access_token, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns a JWT token upon successful authentication"""
    try:
        user = await authenticate_user(form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},  # Using user ID as subject
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during login: {str(e)}"
        ) from e


@router.post("/signin", response_model=DataResponse[User])
async def create_user(user: UserCreate):
    """Create a new user account"""
    try:
        # Create the user via service
        created_user = await create_user_service(user)

        # Convert to response format
        user_response = User(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
            is_admin=created_user.is_admin,
        )

        return DataResponse[User](
            success=True, message="User created successfully", data=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400 if "already" in str(e) else 500,
            detail=f"Error creating user: {str(e)}",
        ) from e


@router.get("/me", response_model=DataResponse[User])
async def get_current_user_profile(current_user: str = Depends(get_current_user)):
    """Get the current user's profile based on the authentication token"""
    try:
        user_id = int(current_user)

        user = await get_current_user_profile_service(user_id)

        return DataResponse[User](
            success=True, message="Profile retrieved successfully", data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving profile: {str(e)}"
        ) from e


@router.put("/me", response_model=DataResponse[User])
async def update_current_user_profile(
    user_update: UserUpdate, current_user: str = Depends(get_current_user)
):
    """Update the current user's profile based on the authentication token"""
    try:
        user_id = int(current_user)

        # Update the user via service
        updated_user_obj = await update_user_profile_service(user_id, user_update)

        updated_user = User(
            id=updated_user_obj.id,
            username=updated_user_obj.username,
            email=updated_user_obj.email,
            full_name=updated_user_obj.full_name,
            is_active=updated_user_obj.is_active,
            created_at=updated_user_obj.created_at,
            updated_at=updated_user_obj.updated_at,
            # head_pic=updated_user_obj.head_pic,
            is_admin=updated_user_obj.is_admin,
        )

        return DataResponse[User](
            success=True, message="Profile updated successfully", data=updated_user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400 if "already" in str(e) else 500,
            detail=f"Error updating profile: {str(e)}",
        ) from e


@router.delete("/me", response_model=DataResponse[bool])
async def delete_current_user_account(
    current_user: str = Depends(get_current_user),
):
    """Delete the current user's account based on the authentication token"""
    try:
        user_id = int(current_user)

        # Delete the user account via service
        success = await delete_user_account_service(user_id)

        return DataResponse[bool](
            success=True, message="Account deactivated successfully", data=success
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting account: {str(e)}",
        ) from e
