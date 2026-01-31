"""
Database module for the Face Recognition System.

This module initializes and manages database connections for both
Milvus (vector database for face features) and SQL databases.
"""

from .init_milvus import FACE_FEATURES_COLLECTION, get_milvus_client
from .init_milvus import init_db as init_milvus
from .init_sql import TORTOISE_ORM
from .init_sql import init_db as init_sql

__ALL__ = [
    "init_milvus",
    "init_sql",
    "TORTOISE_ORM",
    "get_milvus_client",
    "FACE_FEATURES_COLLECTION",
]
