"""
JWT utility module for creating and verifying JWT tokens for authentication.
"""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from ..core import _CONFIG_

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{_CONFIG_.API_V1_STR}/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the given data and expiration time.

    Args:
        data: The data to include in the token
        expires_delta: Optional expiration time for the token

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=_CONFIG_.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Explicitly use HS256 algorithm from settings
    encoded_jwt = jwt.encode(
        to_encode, _CONFIG_.JWT_SECRET_KEY, algorithm=_CONFIG_.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user from the provided token.

    Args:
        token: The JWT token from the Authorization header

    Returns:
        The user identifier from the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Explicitly specify HS256 algorithm from settings
        payload = jwt.decode(
            token, _CONFIG_.JWT_SECRET_KEY, algorithms=[_CONFIG_.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    return user_id


async def get_current_active_user(current_user: str = Depends(get_current_user)):
    """
    Get the current active user, checking that they are active.

    Args:
        current_user: The user identifier from the token

    Returns:
        The current active user

    Raises:
        HTTPException: If the user is inactive
    """
    # In a real application, you would fetch user details from the database
    # and check if they are active. For now, we just return the user ID.
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
