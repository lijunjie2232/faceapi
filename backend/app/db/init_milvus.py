import logging
from multiprocessing import connection
from typing import Optional

from loguru import logger
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusClient,
    connections,
    utility,
)

from ..core import _CONFIG_

# Define collection names
FACE_FEATURES_COLLECTION = "face_features"
USER_ACCOUNTS_COLLECTION = "user_accounts"

# Global Milvus client instance
milvus_client = None


async def init_db():
    """Initialize database connections and create collections if they don't exist"""
    global milvus_client

    try:
        # First connect without database to create the database if it doesn't exist
        connections.connect(
            alias="default",
            host=_CONFIG_.MILVUS_HOST,
            port=_CONFIG_.MILVUS_PORT,
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
        )

        # Create the database if it doesn't exist
        temp_client = MilvusClient(
            uri=f"http://{_CONFIG_.MILVUS_HOST}:{_CONFIG_.MILVUS_PORT}",
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
        )

        # Check if database exists, if not create it
        existing_dbs = temp_client.list_databases()
        if _CONFIG_.MILVUS_DB_NAME not in existing_dbs:
            logger.info(
                f"Database {_CONFIG_.MILVUS_DB_NAME} does not exist, creating it..."
            )
            temp_client.create_database(_CONFIG_.MILVUS_DB_NAME)

        # Now connect to the specific database
        connections.disconnect("default")
        connections.connect(
            alias="default",
            host=_CONFIG_.MILVUS_HOST,
            port=_CONFIG_.MILVUS_PORT,
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
            db_name=_CONFIG_.MILVUS_DB_NAME,
        )

        # Initialize the global Milvus client connected to the specific database
        milvus_client = MilvusClient(
            uri=f"http://{_CONFIG_.MILVUS_HOST}:{_CONFIG_.MILVUS_PORT}",
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
            db_name=_CONFIG_.MILVUS_DB_NAME,
        )

        logger.info("Connected to Milvus successfully")

        # Create face features collection if it doesn't exist
        await create_face_features_collection()

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def create_face_features_collection():
    """Create the face features collection in Milvus"""
    if utility.has_collection(FACE_FEATURES_COLLECTION):
        logger.info(f"Collection {FACE_FEATURES_COLLECTION} already exists")
        return

    # Define the schema for storing face features
    fields = [
        FieldSchema(
            name="user_id",
            dtype=DataType.INT64,
            is_primary=True,
        ),
        FieldSchema(
            name="feature_vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=512,
        ),  # Assuming 512-dim face encoding
        FieldSchema(
            name="update_at",
            dtype=DataType.INT64,
        ),
    ]

    schema = CollectionSchema(
        fields=fields, description="Face feature vectors for recognition"
    )

    face_features_collection = Collection(name=FACE_FEATURES_COLLECTION, schema=schema)

    # Create index for the feature vector field
    index_params = {
        "index_type": "FLAT",
        "metric_type": "COSINE",
    }

    # Create index - this is a synchronous operation in pymilvus
    result = face_features_collection.create_index(
        field_name="feature_vector",
        index_params=index_params,
    )

    logger.info(f"Created collection {FACE_FEATURES_COLLECTION}")

    return face_features_collection


def get_milvus_client():
    """Return the global Milvus client instance"""
    global milvus_client
    if milvus_client is None:
        raise RuntimeError("Milvus client not initialized. Call init_db() first.")
    return milvus_client
