"""
顔認識システムのデータベースモジュール。

このモジュールは顔特徴用のベクトルデータベースであるMilvusと
SQLデータベースの両方のデータベース接続を初期化および管理します。
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
