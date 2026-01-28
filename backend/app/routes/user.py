import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import IntegrityError

from ..core import _CONFIG_
from ..models.user import UserModel
from ..schemas import DataResponse, ListResponse, User, UserCreate, UserUpdate
from ..utils.jwt_utils import create_access_token, get_current_user
from ..utils.pass_utils import hash_password, verify_password

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns a JWT token upon successful authentication"""
    try:
        # Find user by username or email
        user = await UserModel.get_or_none(
            username=form_data.username
        ) or await UserModel.get_or_none(email=form_data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(
            plain_password=form_data.password,
            hashed_password=user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},  # Using user ID as subject
            expires_delta=access_token_expires,
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@router.post("/signin", response_model=DataResponse[User])
async def create_user(user: UserCreate):
    """Create a new user account"""
    try:
        # Check if user already exists
        existing_user = await UserModel.get_or_none(username=user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        existing_email = await UserModel.get_or_none(email=user.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password using the pass_utils module
        hashed_password = hash_password(user.password)

        # Create the user in the database
        created_user = await UserModel.create(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=True,
        )

        # Convert to response format
        user_response = User(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )

        return DataResponse[User](
            success=True, message="User created successfully", data=user_response
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/me", response_model=DataResponse[User])
async def get_current_user_profile(current_user: str = Depends(get_current_user)):
    """Get the current user's profile based on the authentication token"""
    try:
        user_id = int(current_user)
        user_obj = await UserModel.get_or_none(id=user_id)

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        user = User(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
            full_name=user_obj.full_name,
            is_active=user_obj.is_active,
            created_at=user_obj.created_at,
            updated_at=user_obj.updated_at,
        )

        return DataResponse[User](
            success=True, message="Profile retrieved successfully", data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving profile: {str(e)}"
        )


@router.put("/me", response_model=DataResponse[User])
async def update_current_user_profile(
    user_update: UserUpdate, current_user: str = Depends(get_current_user)
):
    """Update the current user's profile based on the authentication token"""
    try:
        user_id = int(current_user)

        # Get the current user to check if it exists
        current_user_obj = await UserModel.get_or_none(id=user_id)

        if not current_user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if username or email already exists for other users
        if user_update.username:
            existing_user_with_username = await UserModel.get_or_none(
                username=user_update.username
            )
            if (
                existing_user_with_username
                and existing_user_with_username.id != user_id
            ):
                raise HTTPException(status_code=400, detail="Username already taken")

        if user_update.email:
            existing_user_with_email = await UserModel.get_or_none(
                email=user_update.email
            )
            if existing_user_with_email and existing_user_with_email.id != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        # Prepare update data
        update_data = {}
        if user_update.username:
            update_data["username"] = user_update.username
        if user_update.email:
            update_data["email"] = user_update.email
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name
        if user_update.password:
            update_data["hashed_password"] = hash_password(user_update.password)
        # if user_update.is_active is not None:
        #     update_data["is_active"] = user_update.is_active
        # not allow change active status by user

        # Update the user
        await UserModel.filter(id=user_id).update(**update_data)

        # Get the updated user
        updated_user_obj = await UserModel.get(id=user_id)

        updated_user = User(
            id=updated_user_obj.id,
            username=updated_user_obj.username,
            email=updated_user_obj.email,
            full_name=updated_user_obj.full_name,
            is_active=updated_user_obj.is_active,
            created_at=updated_user_obj.created_at,
            updated_at=updated_user_obj.updated_at,
        )

        return DataResponse[User](
            success=True, message="Profile updated successfully", data=updated_user
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error updating profile: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.delete("/me", response_model=DataResponse[bool])
async def delete_current_user_account(current_user: str = Depends(get_current_user)):
    """Delete the current user's account based on the authentication token"""
    try:
        user_id = int(current_user)

        # Get the user to check if it exists
        user = await UserModel.get_or_none(id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Deactivate the user instead of hard deleting
        await UserModel.filter(id=user_id).update(is_active=False)

        return DataResponse[bool](
            success=True, message="Account deactivated successfully", data=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting account: {str(e)}")


@router.get("/", response_model=ListResponse[User])
async def list_users(
    skip: int = 0, limit: int = 100, current_user: str = Depends(get_current_user)
):
    """List users with pagination"""
    try:
        # Query users with pagination
        users_queryset = UserModel.all().offset(skip).limit(limit)
        count = await UserModel.all().count()
        users_list = await users_queryset

        users = []
        for user_obj in users_list:
            user = User(
                id=user_obj.id,
                username=user_obj.username,
                email=user_obj.email,
                full_name=user_obj.full_name,
                is_active=user_obj.is_active,
                created_at=user_obj.created_at,
                updated_at=user_obj.updated_at,
            )
            users.append(user)

        return ListResponse[User](
            success=True,
            message="Users retrieved successfully",
            data=users,
            total=count,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")
