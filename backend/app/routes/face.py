import base64
import io
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from traceback import print_exc
import cv2
import numpy as np
import torch
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pymilvus import Collection, MilvusClient

from ..core.config import Config
from ..db import FACE_FEATURES_COLLECTION, get_milvus_client
from ..schemas.face import (
    FaceRecognitionRequest,
    FaceRecognitionResponse,
    FaceRecognitionResult,
    FaceRegisterRequest,
)
from ..schemas.response import DataResponse
from ..utils import (
    create_access_token,
    get_current_user,
    detect_face,
    load_collection,
    inference,
)
from ..face_rec import _MODEL_ as model

# Get config instance
_CONFIG_ = Config()

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
        # Read image file
        contents = await image.read()

        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

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
        access_token_expires = timedelta(minutes=_CONFIG_.ACCESS_TOKEN_EXPIRE_MINUTES)
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

    except HTTPException:
        raise
    except Exception as e:
        print_exc()
        logger.error(f"Error in face verification: {str(e)}")
        # raise HTTPException(
        #     status_code=500, detail=f"Error processing face verification: {str(e)}"
        # )
        raise e


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

        # Delete old embeddings for this user
        delete_result = milvus_client.delete(
            collection_name=FACE_FEATURES_COLLECTION, filter=f"user_id == {user_id}"
        )

        # Insert the new face feature into the collection
        entities = [
            {
                "user_id": user_id,
                "feature_vector": features[0].tolist(),
                "update_at": int(
                    time.time() * 1000
                ),  # Convert to milliseconds since epoch
            }
        ]

        insert_result = milvus_client.insert(
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

        return {
            "success": True,
            "message": f"Face embedding updated successfully for user ID {user_id}",
            "new_embedding_id": inserted_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        print_exc()
        logger.error(f"Error in face embedding update: {str(e)}")
        # raise HTTPException(
        #     status_code=500, detail=f"Error updating face embedding: {str(e)}"
        # )
        raise e
