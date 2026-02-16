"""
顔認識システムの設定モジュール。

このモジュールはアプリケーションのすべての設定を処理するConfigクラスを定義します。
データベース接続、モデルパラメータ、セキュリティ設定などが含まれます。
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Config(BaseSettings):

    CONFIGURABLE_FIELDS = [
        "MILVUS_DB_HOST",
        "MILVUS_DB_PORT",
        "MILVUS_DB_USER",
        "MILVUS_DB_PASSWORD",
        "MILVUS_DB_DB_NAME",
        "SQL_BACKEND",
        "SQL_HOST",
        "SQL_PORT",
        "SQL_USERNAME",
        "SQL_PASSWORD",
        "SQL_DATABASE",
        "MODEL_PATH",
        "MODEL_LOADER",
        "MODEL_THRESHOLD",
        "MODEL_DEVICE",
        "EMB_DIM",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "PASSWORD_HASH_ALGORITHM",
        "LISTEN_HOST",
        "LISTEN_PORT",
        "ALLOWED_ORIGINS",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
        "ADMIN_EMAIL",
        "ADMIN_FULL_NAME",
        "STRICT_MODE",
        "ALLOW_FACE_DEDUPICATION",
    ]

    """
    顔認識システムの設定クラス。

    このクラスにはアプリケーションのすべての設定が含まれています。
    データベース接続、モデルパラメータ、セキュリティ設定などがあります。
    設定は環境変数から読み込むことができます。
    """

    # Milvus設定
    MILVUS_DB_HOST: str = Field(
        os.getenv("MILVUS_DB_HOST", "localhost"), description="Milvusデータベースホスト"
    )
    MILVUS_DB_PORT: int = Field(
        int(os.getenv("MILVUS_DB_PORT", "19530")),
        description="Milvusデータベースポート番号",
    )
    MILVUS_DB_USER: str = Field(
        os.getenv("MILVUS_DB_USER", ""), description="Milvusデータベースユーザー名"
    )
    MILVUS_DB_PASSWORD: str = Field(
        os.getenv("MILVUS_DB_PASSWORD", ""), description="Milvusデータベースパスワード"
    )
    MILVUS_DB_DB_NAME: str = Field(
        os.getenv("MILVUS_DB_DB_NAME", "default"), description="Milvusデータベース名"
    )

    # Sql設定
    SQL_BACKEND: str = Field(
        os.getenv("SQL_BACKEND", "sqlite"),
        description="SQLデータベースバックエンド (sqlite, mysql, postgresql)",
    )
    SQL_HOST: str = Field(
        os.getenv("SQL_HOST", "localhost"), description="SQLデータベースホスト"
    )
    SQL_PORT: int = Field(
        int(os.getenv("SQL_PORT", "3306")), description="SQLデータベースポート番号"
    )
    SQL_USERNAME: str = Field(
        os.getenv("SQL_USERNAME", "root"), description="SQLデータベースユーザー名"
    )
    SQL_PASSWORD: str = Field(
        os.getenv("SQL_PASSWORD", "root"), description="SQLデータベースパスワード"
    )
    SQL_DATABASE: str = Field(
        os.getenv("SQL_DATABASE", "faceapi"), description="SQLデータベース名"
    )

    # モデル設定
    MODEL_PATH: str = Field(
        os.getenv("MODEL_PATH", "./models"), description="モデルファイルへのパス"
    )
    MODEL_LOADER: str = Field(
        os.getenv("MODEL_LOADER", "facenet"), description="使用するモデルローダーの種類"
    )
    MODEL_THRESHOLD: float = Field(
        float(os.getenv("MODEL_THRESHOLD", "0.3")), description="顔認識信頼度の閾値"
    )
    MODEL_DEVICE: str = Field(
        os.getenv("MODEL_DEVICE", "cuda:0"),
        description="モデル推論に使用するデバイス (cpu, cuda:0, cuda:1, etc.)",
    )
    MODEL_EMB_DIM: int = Field(
        int(os.getenv("EMB_DIM", "512")), description="モデルの埋め込み次元数"
    )

    # アプリケーション設定
    API_V1_STR: str = Field("/api/v1", description="APIのバージョンプレフィックス")
    PROJECT_NAME: str = Field("Face Recognition System", description="プロジェクト名")

    # セキュリティ設定
    JWT_SECRET_KEY: str = Field(
        os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        description="JWTトークンのシークレットキー",
    )
    JWT_ALGORITHM: str = Field(
        os.getenv("ALGORITHM", "HS256"), description="JWTトークンのアルゴリズム"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="アクセストークンの有効期限（分）"
    )

    # パスワードハッシュ設定
    PASSWORD_HASH_ALGORITHM: str = Field(
        os.getenv("PASSWORD_HASH_ALGORITHM", "sha256_crypt"),
        description="パスワードハッシュのアルゴリズム",
    )

    # 顔認識設定
    # FACE_DETECTION_MODEL: str = "hog"  # オプション: "hog", "cnn"
    # TOLERANCE: float = 0.6  # 値が小さいほど厳密なマッチング

    # STRICT_MODEでは、顔とユーザー名・パスワードの両方を検証する必要があります
    STRICT_MODE: bool = Field(
        True, description="厳格モード（顔認証と資格情報の両方を検証）"
    )

    # サーバー設定
    LISTEN_HOST: str = Field(
        os.getenv("LISTEN_HOST", "0.0.0.0"), description="サーバーのリッスンホスト"
    )
    LISTEN_PORT: int = Field(
        int(os.getenv("LISTEN_PORT", "8000")), description="サーバーのリッスンポート"
    )

    # CORSの許可オリジン
    ALLOWED_ORIGINS: list[str] = Field([], description="CORS許可オリジンリスト")

    # default init account
    ADMIN_USERNAME: str = Field(
        os.getenv("ADMIN_USERNAME", "admin"), description="初期管理者ユーザー名"
    )
    ADMIN_PASSWORD: str = Field(
        os.getenv("ADMIN_PASSWORD", "admin"), description="初期管理者パスワード"
    )
    ADMIN_EMAIL: str = Field(
        os.getenv("ADMIN_EMAIL", "admin@example.com"),
        description="初期管理者メールアドレス",
    )
    ADMIN_FULL_NAME: str = Field(
        os.getenv("ADMIN_FULL_NAME", "Administrator"), description="初期管理者氏名"
    )
    # システム設定
    ALLOW_FACE_DEDUPICATION: bool = Field(
        True, description="顔の重複検出を許可するかどうか"
    )
    # class Config:
    #     """環境ファイル設定を定義するPydantic設定クラス。"""

    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev", ".env.prod"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
