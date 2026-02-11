"""
顔認識システムのデータベースモジュール。

このモジュールは顔特徴用のベクトルデータベースであるMilvusと
SQLデータベースの両方のデータベース接続を初期化および管理します。
"""

from .init_milvus import FACE_FEATURES_COLLECTION, get_milvus_client
from .init_milvus import init_db as milvus_init
from .init_sql import TORTOISE_ORM
from .init_sql import init_db as sql_init
from .init_account import create_init_account


__ALL__ = [
    "milvus_init",
    "sql_init",
    "TORTOISE_ORM",
    "get_milvus_client",
    "FACE_FEATURES_COLLECTION",
    "create_init_account",
]
