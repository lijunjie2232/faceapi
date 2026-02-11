"""
Admin service module for the Face Recognition System.

This module contains business logic for administrative operations
including user management functionalities.
"""

from typing import List, Optional

from ..db import FACE_FEATURES_COLLECTION, get_milvus_client
from ..models.user import UserModel
from ..schemas import BatchOperationResult, User, UserCreateAsAdmin, UserUpdateAsAdmin
from ..utils import hash_password, load_collection


async def list_users_service(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    set_face: Optional[bool] = None,
):
    """
    Service function to list all users with pagination.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        username: Optional filter for username (case-insensitive partial match)
        email: Optional filter for email (case-insensitive partial match)
        full_name: Optional filter for full name (case-insensitive partial match)
        is_active: Optional filter for active status
        is_admin: Optional filter for admin status
        set_face: Optional filter for face picture status (True if face pic is set, False if not)

    Returns:
        A tuple containing the list of users and the total count
    """
    from tortoise.expressions import Q

    # Build the query with filters if any filter is provided
    users_queryset = UserModel.all()
    filter_condition = Q()  # Start with an empty condition

    if username is not None:
        filter_condition &= Q(username__icontains=username)
    if email is not None:
        filter_condition &= Q(email__icontains=email)
    if full_name is not None:
        filter_condition &= Q(full_name__icontains=full_name)
    if is_active is not None:
        filter_condition &= Q(is_active=is_active)
    if is_admin is not None:
        filter_condition &= Q(is_admin=is_admin)
    if set_face is not None:
        if set_face:
            filter_condition &= ~Q(head_pic=None)  # Not null (face pic is set)
        else:
            filter_condition &= Q(head_pic=None)  # Is null (no face pic set)

    # Apply the combined filter
    users_queryset = users_queryset.filter(filter_condition)

    # Get the count with the same filter conditions
    count = await users_queryset.count()

    # Apply pagination
    users_list = await users_queryset.offset(skip).limit(limit)

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


async def batch_reset_password_service(
    user_ids: List[int], new_password: str
) -> BatchOperationResult:
    """
    Service function to reset passwords for multiple users.

    Args:
        user_ids: List of user IDs to reset passwords for
        new_password: New password to set for all users

    Returns:
        BatchOperationResult containing success/failure statistics
    """
    success_count = 0
    failed_users = []

    hashed_password = hash_password(new_password)

    for user_id in user_ids:
        try:
            result = await UserModel.filter(id=user_id).update(
                hashed_password=hashed_password
            )
            if result > 0:
                success_count += 1
            else:
                failed_users.append(user_id)
        except Exception:
            failed_users.append(user_id)

    return BatchOperationResult(
        success_count=success_count,
        failed_count=len(failed_users),
        total_count=len(user_ids),
        failed_users=failed_users,
        operation="reset-password",
    )


async def batch_activate_users_service(user_ids: List[int]) -> BatchOperationResult:
    """
    Service function to activate multiple users.

    Args:
        user_ids: List of user IDs to activate

    Returns:
        BatchOperationResult containing success/failure statistics
    """
    success_count = 0
    failed_users = []

    for user_id in user_ids:
        try:
            result = await UserModel.filter(id=user_id).update(is_active=True)
            if result > 0:
                success_count += 1
            else:
                failed_users.append(user_id)
        except Exception:
            failed_users.append(user_id)

    return BatchOperationResult(
        success_count=success_count,
        failed_count=len(failed_users),
        total_count=len(user_ids),
        failed_users=failed_users,
        operation="active",
    )


async def batch_deactivate_users_service(user_ids: List[int]) -> BatchOperationResult:
    """
    Service function to deactivate multiple users.

    Args:
        user_ids: List of user IDs to deactivate

    Returns:
        BatchOperationResult containing success/failure statistics
    """
    success_count = 0
    failed_users = []

    for user_id in user_ids:
        try:
            result = await UserModel.filter(id=user_id).update(is_active=False)
            if result > 0:
                success_count += 1
            else:
                failed_users.append(user_id)
        except Exception:
            failed_users.append(user_id)

    return BatchOperationResult(
        success_count=success_count,
        failed_count=len(failed_users),
        total_count=len(user_ids),
        failed_users=failed_users,
        operation="inactive",
    )


async def batch_reset_face_data_service(user_ids: List[int]) -> BatchOperationResult:
    """
    Service function to reset face data for multiple users.

    Args:
        user_ids: List of user IDs to reset face data for

    Returns:
        BatchOperationResult containing success/failure statistics
    """
    success_count = 0
    failed_users = []
    # Get the shared Milvus client
    milvus_client = get_milvus_client()

    await load_collection(FACE_FEATURES_COLLECTION)

    for user_id in user_ids:
        try:
            result = await UserModel.filter(id=user_id).update(head_pic=None)

            if result > 0:
                success_count += 1
            else:
                failed_users.append(user_id)

            milvus_client.delete(
                collection_name=FACE_FEATURES_COLLECTION,
                ids=[user_id],
            )

        except Exception:
            failed_users.append(user_id)

    return BatchOperationResult(
        success_count=success_count,
        failed_count=len(failed_users),
        total_count=len(user_ids),
        failed_users=failed_users,
        operation="reset-face",
    )
