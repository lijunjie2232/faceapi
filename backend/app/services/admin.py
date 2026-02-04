"""
Admin service module for the Face Recognition System.

This module contains business logic for administrative operations
including user management functionalities.
"""

from ..models.user import UserModel
from ..schemas import User, UserCreateAsAdmin, UserUpdateAsAdmin
from ..utils.pass_utils import hash_password


async def list_users_service(skip: int = 0, limit: int = 100):
    """
    Service function to list all users with pagination.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return

    Returns:
        A tuple containing the list of users and the total count
    """
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
            # head_pic=user_obj.head_pic,
            head_pic="1" if user_obj.head_pic else "0",
            is_admin=user_obj.is_admin,
        )
        users.append(user)

    return users, count


async def create_user_as_admin_service(user_create: UserCreateAsAdmin):
    """
    Service function to create a new user as admin.

    Args:
        user_create: User creation request object containing user details

    Returns:
        Created user object
    """
    # Hash the password
    hashed_password = hash_password(user_create.password)

    # Create the user in the database
    created_user = await UserModel.create(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=user_create.is_admin,
    )

    return created_user


async def update_user_as_admin_service(user_id: int, user_update: UserUpdateAsAdmin):
    """
    Service function to update a specific user by ID.

    Args:
        user_id: The ID of the user to update
        user_update: User update request object containing fields to update

    Returns:
        Updated user object
    """
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
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active
    if user_update.is_admin is not None:
        update_data["is_admin"] = user_update.is_admin

    # Update the user
    await UserModel.filter(id=user_id).update(**update_data)

    # Get the updated user
    updated_user = await UserModel.get(id=user_id)

    return updated_user


async def deactivate_user_service(user_id: int):
    """
    Service function to deactivate a specific user by ID.

    Args:
        user_id: The ID of the user to deactivate

    Returns:
        Boolean indicating success
    """
    # Perform soft delete by deactivating the user
    result = await UserModel.filter(id=user_id).update(is_active=False)
    return result > 0


async def activate_user_service(user_id: int):
    """
    Service function to activate a specific user by ID.

    Args:
        user_id: The ID of the user to activate

    Returns:
        Boolean indicating success
    """
    # Activate the user
    result = await UserModel.filter(id=user_id).update(is_active=True)
    return result > 0


async def validate_user_update_uniqueness(user_id: int, user_update: UserUpdateAsAdmin):
    """
    Validate that updated username/email don't conflict with other users.

    Args:
        user_id: The ID of the user being updated
        user_update: User update request object containing fields to update

    Returns:
        Error message if validation fails, None otherwise
    """
    if user_update.username:
        existing_user_with_username = await UserModel.get_or_none(
            username=user_update.username
        )
        if existing_user_with_username and existing_user_with_username.id != user_id:
            return "Username already taken"

    if user_update.email:
        existing_user_with_email = await UserModel.get_or_none(email=user_update.email)
        if existing_user_with_email and existing_user_with_email.id != user_id:
            return "Email already registered"

    return None
