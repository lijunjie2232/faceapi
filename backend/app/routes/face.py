"""
Face recognition routes module for the Face Recognition System.

This module defines the API endpoints for face registration, recognition,
and verification functionalities of the application.
"""

import logging
from traceback import print_exc

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from tortoise.transactions import atomic

from ..services.face import update_face_embedding_service, verify_face_service
from ..utils import get_current_user

router = APIRouter(
    prefix="/face",
    tags=["face"],
)
logger = logging.getLogger(__name__)


@router.post("/verify")
async def verify_face(
    image: UploadFile = File(...),
):
    """
    Verify a face from uploaded image and return either a denial result or an OAuth2 token.

    Args:
        image: Uploaded image file containing a face

    Returns:
        Either a denial message or an OAuth2 token if face is recognized
    """
    try:
        result = await verify_face_service(image)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print_exc()
        logger.error("Error in face verification: %s", str(e))
        raise e


@atomic()
@router.put("/me", dependencies=[Depends(get_current_user)])
async def update_face_embedding(
    image: UploadFile = File(...), current_user: str = Depends(get_current_user)
):
    """
    Update the face embedding for the currently authenticated user.
    Requires OAuth2 authentication, similar to user API.

    Args:
        image: Uploaded image file containing the new face
        current_user: The currently authenticated user (from JWT token)

    Returns:
        Success message indicating the embedding was updated
    """
    try:
        # Get user ID from the token
        user_id = int(current_user)

        result = await update_face_embedding_service(user_id, image)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print_exc()
        logger.error("Error in face embedding update: %s", str(e))
        raise e
