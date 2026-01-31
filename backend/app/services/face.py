"""
Face service module for the Face Recognition System.

This module contains business logic for face recognition operations
including face verification and embedding updates.
"""

import time
from typing import Any, Dict

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile

from ..core.config import Config
from ..db import FACE_FEATURES_COLLECTION, get_milvus_client
from ..face_rec import _MODEL_ as model
from ..models import UserModel
from ..utils import (
    create_access_token,
    detect_face,
    image_to_base64,
    inference,
    load_collection,
)

# Get config instance
_CONFIG_ = Config()


async def verify_face_service(image: UploadFile) -> Dict[str, Any]:
    """
    Service function to verify a face from uploaded image.

    Args:
        image: Uploaded image file containing a face

    Returns:
        Dictionary containing recognition result and token if successful
    """
    # Read image file
    contents = await image.read()

    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    # pylint: disable=no-member
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # pylint: enable=no-member

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Detect faces in the image
    detected_faces = detect_face(img)

    if not detected_faces:
        return {
            "recognized": False,
            "message": "No face detected in the image",
            "token": None,
        }

    # Extract features from the face
    features = [
        inference(model, face_img, device=_CONFIG_.MODEL_DEVICE).reshape(512)
        for face_img in detected_faces
    ]

    # Get the shared Milvus client
    milvus_client = get_milvus_client()

    await load_collection(FACE_FEATURES_COLLECTION)

    # Search for similar faces in the collection
    search_results = milvus_client.search(
        collection_name=FACE_FEATURES_COLLECTION,
        data=features,
        limit=1,  # Only need the closest match
        output_fields=["user_id"],
        search_params={
            "metric_type": "COSINE",
            "params": {"radius": _CONFIG_.MODEL_THRESHOLD},
        },
    )
    if not any(search_results):
        # No matching face found
        return {
            "recognized": False,
            "message": "Face not recognized in the database",
            "token": None,
            "token_type": "bearer",
        }

    # Get the best match
    # best_match = search_results[0][0]
    best_match = list(filter(lambda l: len(l) > 0, search_results))[0][0]

    # Face recognized, get user info and create token
    user_id = best_match["entity"]["user_id"]

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user_id)},
    )

    return {
        "recognized": True,
        "message": f"Face recognized as user(id={user_id})",
        "user_id": user_id,
        "confidence": 1 - best_match["distance"],  # Convert distance to similarity
        "token": access_token,
    }


async def update_face_embedding_service(
    user_id: int, image: UploadFile
) -> Dict[str, Any]:
    """
    Service function to update the face embedding for a user.

    Args:
        user_id: ID of the user whose face embedding to update
        image: Uploaded image file containing the new face

    Returns:
        Dictionary containing success message and embedding ID
    """
    # Read image file
    contents = await image.read()

    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    # pylint: disable=no-member
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # pylint: enable=no-member

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Get user object
    user = await UserModel.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Detect faces in the image
    detected_faces = detect_face(img)

    if not detected_faces:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    if len(detected_faces) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple faces detected. Please upload an image with only one face.",
        )

    # Process the first detected face
    face_img = detected_faces[0]

    # Extract features from the face
    features = inference(model, face_img, device=_CONFIG_.MODEL_DEVICE)

    # Get the shared Milvus client
    milvus_client = get_milvus_client()

    await load_collection(FACE_FEATURES_COLLECTION)

    # Insert the new face feature into the collection
    entities = [
        {
            "user_id": user_id,
            "feature_vector": features[0].tolist(),
            "update_at": int(time.time() * 1000),  # Convert to milliseconds since epoch
        }
    ]

    insert_result = milvus_client.upsert(
        collection_name=FACE_FEATURES_COLLECTION, data=entities
    )

    # Handle potential response variations from Milvus client
    inserted_id = None
    if isinstance(insert_result, dict):
        # Check for different possible keys in the response
        if "insertedIds" in insert_result:
            inserted_id = (
                insert_result["insertedIds"][0]
                if insert_result["insertedIds"]
                else None
            )
        elif "inserted_ids" in insert_result:
            inserted_id = (
                insert_result["inserted_ids"][0]
                if insert_result["inserted_ids"]
                else None
            )
    elif hasattr(insert_result, "inserted_ids"):
        inserted_id = (
            insert_result.inserted_ids[0] if insert_result.inserted_ids else None
        )

    # update picture in bytes in sql
    user.head_pic = image_to_base64(img)
    await user.save()

    return {
        "success": True,
        "message": f"Face embedding updated successfully for user ID {user_id}",
        "new_embedding_id": inserted_id,
    }
