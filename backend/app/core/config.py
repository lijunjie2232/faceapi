"""
顔認識システムの設定モジュール。

このモジュールはアプリケーションのすべての設定を処理するConfigクラスを定義します。
データベース接続、モデルパラメータ、セキュリティ設定などが含まれます。
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Config(BaseSettings):
    """
    顔認識システムの設定クラス。

    このクラスにはアプリケーションのすべての設定が含まれています。
    データベース接続、モデルパラメータ、セキュリティ設定などがあります。
    設定は環境変数から読み込むことができます。
    """

    # Milvus設定
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_USER: str = os.getenv("MILVUS_USER", "")
    MILVUS_PASSWORD: str = os.getenv("MILVUS_PASSWORD", "")
    MILVUS_DB_NAME: str = os.getenv(
        "MILVUS_DB_NAME", "default"
    )  # Milvus DB名の新しい設定

    # Sql設定
    SQL_BACKEND: str = os.getenv("SQL_BACKEND", "sqlite")
    SQL_HOST: str = os.getenv("SQL_HOST", "localhost")
    SQL_PORT: int = int(os.getenv("SQL_PORT", "3306"))
    SQL_USERNAME: str = os.getenv("SQL_USERNAME", "root")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "root")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE", "faceapi")

    # モデル設定
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")  # モデルファイルへのパス
    MODEL_LOADER: str = os.getenv(
        "MODEL_LOADER", "facenet"
    )  # 使用するモデルローダーの種類
    MODEL_THRESHOLD: float = float(
        os.getenv(
            "MODEL_THRESHOLD",
            "0.3",
        )
    )  # 顔認識信頼度の閾値
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cuda:0")
    MODEL_EMB_DIM: int = int(os.getenv("EMB_DIM", "512"))

    # アプリケーション設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Face Recognition System"

    # セキュリティ設定
    JWT_SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("ALGORITHM", "HS256")  # JWTトークンのアルゴリズム
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # パスワードハッシュ設定
    PASSWORD_HASH_ALGORITHM: str = os.getenv(
        "PASSWORD_HASH_ALGORITHM", "sha256_crypt"
    )  # パスワードハッシュのアルゴリズム

    # 顔認識設定
    FACE_DETECTION_MODEL: str = "hog"  # オプション: "hog", "cnn"
    TOLERANCE: float = 0.6  # 値が小さいほど厳密なマッチング

    # STRICT_MODEでは、顔とユーザー名・パスワードの両方を検証する必要があります
    STRICT_MODE: bool = True

    # サーバー設定
    LISTEN_HOST: str = os.getenv("LISTEN_HOST", "0.0.0.0")
    LISTEN_PORT: int = int(os.getenv("LISTEN_PORT", "8000"))

    # CORSの許可オリジン
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",  # デフォルトのVue開発サーバー
        "http://localhost:8080",  # 代替Vue開発サーバー
        "https://localhost",
        "https://localhost:3000",
        "https://localhost:8080",
    ]

    # class Config:
    #     """環境ファイル設定を定義するPydantic設定クラス。"""

    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
    )

    # システム設定
    ALLOW_FACE_DEDUPICATION: bool = True

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file="config.yaml"),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
