import argparse
import re
from pathlib import Path
from typing import Callable

import numpy as np
import torch
import yaml
from pymilvus import DataType, MilvusClient
from StarNet import faceDetector, get_s3, inference

# Default device and model configuration
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "g_m3.pt"


def load_milvus_config(config_path="milvus_config.yaml"):
    """
    Load Milvus configuration from YAML file
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["milvus"]


def load_model(get_sn: Callable, model_path: Path, device: str | torch.device):
    """
    Load the face recognition model and initialize the Milvus client
    """
    # Load the model
    return get_sn(model_path).eval().to(device)


def init_milvus(client):
    """
    init Milvus
    """
    # Load Milvus configuration from YAML
    config = load_milvus_config()

    # Initialize Milvus client
    client = MilvusClient(
        uri=config["uri"],
        token=config["token"],
    )

    if "test" not in client.list_databases():
        client.create_database("test")

    client.use_database("test")

    # Check if collection exists, if not create it
    if not client.has_collection("experiment"):
        create_collection(client)

    # Load the collection
    client.load_collection("experiment")

    # Create schema
    schema = MilvusClient.create_schema()
    schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=512)
    schema.add_field("user_id", DataType.INT64)
    schema.add_field("user_name", DataType.VARCHAR, max_length=200)

    # Create collection
    client.create_collection(
        collection_name="experiment",
        dimension=512,
        metric_type="COSINE",
        schema=schema,
    )

    # Set up the index parameters
    index_params = MilvusClient.prepare_index_params()

    # Add an index on the vector field.
    index_params.add_index(
        field_name="vector",
        metric_type="COSINE",
        index_type="IVF_FLAT",
        index_name="vector_index",
    )

    # Create an index file
    client.create_index(
        collection_name="experiment",
        index_params=index_params,
        sync=False,
    )

    client.flush("experiment")
    print("Created new collection for face recognition")


def add_user_to_database(image_path, user_name, user_id, model, client, device):
    """
    Adds a new user to the face recognition database.

    Args:
        image_path: Path to the image file of the user
        user_name: Name of the user
        user_id: Unique ID for the user
        model: Loaded face recognition model
        client: Milvus client instance
        device: Computing device

    Returns:
        bool: True if user was added successfully, False otherwise
    """
    face_detector = faceDetector()

    # Detect face in the image
    detected_faces = face_detector(image_path)

    if not detected_faces:
        print(f"Error: No face detected in the image: {image_path}")
        return False

    # Extract features from the detected face
    face_img = detected_faces[0]
    features = inference(model, face_img, device=device)

    # Insert into database
    entities = [
        {
            "vector": features[0].tolist(),
            "user_id": int(user_id),
            "user_name": user_name,
        }
    ]

    try:
        insert_result = client.insert(collection_name="experiment", data=entities)
        client.flush("experiment")
        print(f"Successfully added user '{user_name}' (ID: {user_id}) to the database")
        return True
    except Exception as e:
        print(f"Error inserting user into database: {e}")
        return False


def predict_face_identity(
    image_path, model, client: MilvusClient, device, threshold=0.7
):
    """
    Predicts face identity by extracting features from an image and searching for similar faces in the Milvus database.

    Args:
        image_path: Path to the image file
        model: Loaded face recognition model
        client: Milvus client instance
        device: Computing device
        threshold: Confidence threshold for face recognition

    Returns:
        dict: Contains whether face was found, identity and confidence score
    """
    face_detector = faceDetector()

    # Detect face in the image
    detected_faces = face_detector(image_path)

    if not detected_faces:
        return {
            "success": False,
            "found": False,
            "identity": None,
            "confidence": 0.0,
            "message": "No face detected in the image",
        }

    # Extract features from the detected face
    from StarNet import inference

    face_img = detected_faces[0]
    features = inference(model, face_img, device=device)

    # Search in Milvus database for similar faces
    search_result = client.search(
        collection_name="experiment",
        anns_field="vector",
        data=[features[0]],
        limit=3,
        output_fields=["user_id", "user_name"],
        search_params={
            "params": {
                "radius": threshold,  # Using the threshold as radius for search
            },
        },
    )

    if not search_result or len(search_result[0]) == 0:
        return {
            "success": True,
            "found": False,
            "identity": None,
            "confidence": 0.0,
            "message": "No similar face found in the database",
        }

    # Get the top match
    top_match = search_result[0][0]
    similarity_score = top_match.distance  # Convert distance to similarity
    user_id = top_match.entity.get("user_id")
    user_name = top_match.entity.get("user_name")
    return {
        "success": True,
        "found": True,
        "identity": {"user_id": user_id, "user_name": user_name},
        "confidence": similarity_score,
        "message": f"Face found in database. Identity: {user_name} (ID: {user_id})",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Add user to database or predict face identity from an image"
    )
    parser.add_argument("image_path", type=str, help="Path to the image file")

    # Mutually exclusive group for actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--predict",
        action="store_true",
        help="Perform face recognition prediction (default behavior)",
    )
    action_group.add_argument(
        "--add-user",
        nargs=2,
        metavar=("USER_NAME", "USER_ID"),
        help="Add a new user to the database (requires user name and user ID)",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.2285,
        help="Confidence threshold for recognition (default: 0.2285)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        help=f"Computing device (default: {DEVICE})",
    )

    args = parser.parse_args()

    # Validate image path
    img_path = Path(args.image_path)
    if not img_path.exists():
        print(f"Error: Image file does not exist: {args.image_path}")
        return

    # Load model and client
    print("Loading model and connecting to database...")
    try:
        model, client = load_model_and_client()
    except Exception as e:
        print(f"Error loading model or connecting to database: {e}")
        return

    if args.add_user:
        # Add user to database
        user_name, user_id_str = args.add_user

        # Validate user ID is numeric
        try:
            user_id = int(user_id_str)
        except ValueError:
            print(f"Error: User ID must be a number, got: {user_id_str}")
            return

        # Validate user name format
        if not re.match(r"^[A-Za-z0-9 _-]+$", user_name):
            print(f"Error: User name contains invalid characters: {user_name}")
            print(
                "Only alphanumeric characters, spaces, hyphens, and underscores are allowed"
            )
            return

        success = add_user_to_database(
            image_path=args.image_path,
            user_name=user_name,
            user_id=user_id,
            model=model,
            client=client,
            device=args.device,
        )

        if success:
            print(
                f"User '{user_name}' (ID: {user_id}) successfully added to the database!"
            )
        else:
            print("Failed to add user to database.")

    elif args.predict or not (args.add_user):  # Default behavior is prediction
        # Perform prediction
        print(f"Analyzing face in image: {args.image_path}")
        result = predict_face_identity(
            image_path=args.image_path,
            model=model,
            client=client,
            device=args.device,
            threshold=args.threshold,
        )

        # Print results
        print("\nPrediction Result:")
        print(f"Success: {result['success']}")
        print(f"Found in database: {result['found']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Message: {result['message']}")

        if result["identity"]:
            identity = result["identity"]
            print(f"Identity: {identity['user_name']} (ID: {identity['user_id']})")


if __name__ == "__main__":
    main()
