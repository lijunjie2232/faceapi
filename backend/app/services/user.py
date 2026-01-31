"""
User service module for the Face Recognition System.

This module contains business logic for user management
including authentication and profile operations.
"""

from fastapi import HTTPException

from ..models.user import UserModel
from ..schemas import User, UserCreate, UserUpdate
from ..utils import hash_password, verify_password


async def authenticate_user(username: str, password: str):
    """
    Authenticate a user by username/email and password.

    Args:
        username: Username or email of the user
        password: Plain text password to verify

    Returns:
        Authenticated user object if successful, None otherwise
    """
    # Find user by username or email
    user = await UserModel.get_or_none(
        username=username
    ) or await UserModel.get_or_none(email=username)

    if not user:
        return None

    # Check if user is active
    if not user.is_active:
        return None

    # Verify password
    if not verify_password(
        plain_password=password,
        hashed_password=user.hashed_password,
    ):
        return None

    return user


async def create_user_service(user: UserCreate):
    """
    Service function to create a new user.

    Args:
        user: User creation request object containing user details

    Returns:
        Created user object
    """
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

    return created_user


async def get_current_user_profile_service(user_id: int):
    """
    Service function to get the current user's profile.

    Args:
        user_id: ID of the user whose profile to retrieve

    Returns:
        User profile object if found
    """
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
        head_pic=user_obj.head_pic,
        is_admin=user_obj.is_admin,
    )

    return user


async def update_user_profile_service(user_id: int, user_update: UserUpdate):
    """
    Service function to update the current user's profile.

    Args:
        user_id: ID of the user to update
        user_update: User update request object containing fields to update

    Returns:
        Updated user object
    """
    # Get the current user to check if it exists
    current_user_obj = await UserModel.get_or_none(id=user_id)

    if not current_user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if username or email already exists for other users
    if user_update.username:
        existing_user_with_username = await UserModel.get_or_none(
            username=user_update.username
        )
        if existing_user_with_username and existing_user_with_username.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")

    if user_update.email:
        existing_user_with_email = await UserModel.get_or_none(email=user_update.email)
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

    # Update the user
    await UserModel.filter(id=user_id).update(**update_data)

    # Get the updated user
    updated_user_obj = await UserModel.get(id=user_id)

    return updated_user_obj


async def delete_user_account_service(user_id: int):
    """
    Service function to delete (deactivate) the current user's account.

    Args:
        user_id: ID of the user to deactivate

    Returns:
        Boolean indicating success
    """
    # Get the user to check if it exists
    user = await UserModel.get_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Deactivate the user instead of hard deleting
    result = await UserModel.filter(id=user_id).update(is_active=False)

    return result > 0


async def get_user_service(*args, **kwargs):
    """
    Service function to get a specific user by ID.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User object if found, None otherwise
    """
    user = await UserModel.get_or_none(*args, **kwargs)
    return user
