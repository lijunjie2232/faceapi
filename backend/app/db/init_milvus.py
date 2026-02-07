"""
Milvus用データベース初期化モジュール。

このモジュールは顔特徴ベクトルの保存と取得のための
Milvusベクトルデータベースの初期化とセットアップを処理します。
"""

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

# コレクション名を定義
FACE_FEATURES_COLLECTION = "face_features"
USER_ACCOUNTS_COLLECTION = "user_accounts"

# グローバルMilvusクライアントインスタンス
MILVUS_CLIENT = None


async def init_db():
    """データベース接続を初期化し、存在しない場合はコレクションを作成"""
    global MILVUS_CLIENT

    try:
        # 最初にデータベースなしで接続し、存在しない場合はデータベースを作成
        connections.connect(
            alias="default",
            host=_CONFIG_.MILVUS_HOST,
            port=_CONFIG_.MILVUS_PORT,
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
        )

        # 存在しない場合はデータベースを作成
        temp_client = MilvusClient(
            uri=f"http://{_CONFIG_.MILVUS_HOST}:{_CONFIG_.MILVUS_PORT}",
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
        )

        # データベースが存在するか確認し、存在しない場合は作成
        existing_dbs = temp_client.list_databases()
        if _CONFIG_.MILVUS_DB_NAME not in existing_dbs:
            logger.info(
                f"データベース {_CONFIG_.MILVUS_DB_NAME} が存在しないため、作成しています..."
            )
            temp_client.create_database(_CONFIG_.MILVUS_DB_NAME)

        # 特定のデータベースに接続
        connections.disconnect("default")
        connections.connect(
            alias="default",
            host=_CONFIG_.MILVUS_HOST,
            port=_CONFIG_.MILVUS_PORT,
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
            db_name=_CONFIG_.MILVUS_DB_NAME,
        )

        # 特定のデータベースに接続されたグローバルMilvusクライアントを初期化
        MILVUS_CLIENT = MilvusClient(
            uri=f"http://{_CONFIG_.MILVUS_HOST}:{_CONFIG_.MILVUS_PORT}",
            user=_CONFIG_.MILVUS_USER,
            password=_CONFIG_.MILVUS_PASSWORD,
            db_name=_CONFIG_.MILVUS_DB_NAME,
        )

        logger.info("Milvusへの接続に成功しました")

        # 存在しない場合は顔特徴コレクションを作成
        await create_face_features_collection()

    except Exception as e:
        logger.error(f"データベース初期化エラー: {e}")
        raise


async def create_face_features_collection():
    """Milvusに顔特徴コレクションを作成"""
    if utility.has_collection(FACE_FEATURES_COLLECTION):
        logger.info(f"コレクション {FACE_FEATURES_COLLECTION} は既に存在します")
        return

    # 顔特徴を保存するためのスキーマを定義
    fields = [
        FieldSchema(
            name="user_id",
            dtype=DataType.INT64,
            is_primary=True,
        ),
        FieldSchema(
            name="feature_vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=_CONFIG_.MODEL_EMB_DIM,
        ),  # モデルの顔エンコーディング次元
        FieldSchema(
            name="update_at",
            dtype=DataType.INT64,
        ),
    ]

    schema = CollectionSchema(
        fields=fields, description="認識用の顔特徴ベクトル"
    )

    face_features_collection = Collection(name=FACE_FEATURES_COLLECTION, schema=schema)

    # 特徴ベクトルフィールドのインデックスを作成
    index_params = {
        "index_type": "FLAT",
        "metric_type": "COSINE",
    }

    # インデックスを作成 - これはpymilvusでの同期操作です
    await face_features_collection.create_index(
        field_name="feature_vector",
        index_params=index_params,
    )

    logger.info(f"コレクション {FACE_FEATURES_COLLECTION} を作成しました")

    return face_features_collection


def get_milvus_client():
    """グローバルMilvusクライアントインスタンスを返す"""
    if MILVUS_CLIENT is None:
        raise RuntimeError("Milvusクライアントが初期化されていません。まずinit_db()を呼び出してください。")
    return MILVUS_CLIENT
