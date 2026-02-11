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
    # Milvusクライアントを使用してコレクションの存在を確認
    milvus_client = get_milvus_client()

    try:
        # コレクションが存在するか確認
        if FACE_FEATURES_COLLECTION in milvus_client.list_collections():
            logger.info(f"コレクション {FACE_FEATURES_COLLECTION} は既に存在します")
            return
    except Exception:
        # コレクションが存在しない場合やエラーの場合、新しく作成
        pass

    # スキーマを作成
    schema = MilvusClient.create_schema()
    schema.add_field("user_id", DataType.INT64, is_primary=True)
    schema.add_field(
        "feature_vector", DataType.FLOAT_VECTOR, dim=_CONFIG_.MODEL_EMB_DIM
    )
    schema.add_field("update_at", DataType.INT64)

    # コレクションを作成
    milvus_client.create_collection(
        collection_name=FACE_FEATURES_COLLECTION,
        schema=schema,
    )

    # インデックスパラメータを設定
    index_params = MilvusClient.prepare_index_params()

    # ベクトルフィールドにインデックスを追加
    index_params.add_index(
        field_name="feature_vector",
        metric_type="COSINE",
        index_type="FLAT",
        index_name="feature_vector_index",
    )

    # インデックスを作成
    milvus_client.create_index(
        collection_name=FACE_FEATURES_COLLECTION,
        index_params=index_params,
        sync=True,  # 同期的にインデックス作成を待つ
    )

    # コレクションをロード
    milvus_client.load_collection(FACE_FEATURES_COLLECTION)

    logger.info(f"コレクション {FACE_FEATURES_COLLECTION} を作成しました")

    return FACE_FEATURES_COLLECTION


def get_milvus_client():
    """グローバルMilvusクライアントインスタンスを返す"""
    if MILVUS_CLIENT is None:
        raise RuntimeError(
            "Milvusクライアントが初期化されていません。まずinit_db()を呼び出してください。"
        )
    return MILVUS_CLIENT
