"""
Configuration module for Face Recognition System.

This module defines the Config class which handles all the configuration settings
for the application, including database connections, model parameters, and security settings.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Config(BaseSettings):
    """
    Configuration class for the Face Recognition System.

    This class contains all configuration settings for the application,
    including database connections, model parameters, and security settings.
    Settings can be loaded from environment variables.
    """

    # Milvus settings
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_USER: str = os.getenv("MILVUS_USER", "")
    MILVUS_PASSWORD: str = os.getenv("MILVUS_PASSWORD", "")
    MILVUS_DB_NAME: str = os.getenv(
        "MILVUS_DB_NAME", "default"
    )  # New setting for Milvus DB name

    # Sql settings
    SQL_BACKEND: str = os.getenv("SQL_BACKEND", "sqlite")
    SQL_HOST: str = os.getenv("SQL_HOST", "localhost")
    SQL_PORT: int = int(os.getenv("SQL_PORT", "3306"))
    SQL_USERNAME: str = os.getenv("SQL_USERNAME", "root")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "root")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE", "faceapi")

    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")  # Path to model files
    MODEL_LOADER: str = os.getenv(
        "MODEL_LOADER", "facenet"
    )  # Type of model loader to use
    MODEL_THRESHOLD: float = float(
        os.getenv(
            "MODEL_THRESHOLD",
            "0.3",
        )
    )  # Threshold for face recognition confidence
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cuda:0")

    # Application settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Face Recognition System"

    # Security settings
    JWT_SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("ALGORITHM", "HS256")  # Algorithm for JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Password hashing settings
    PASSWORD_HASH_ALGORITHM: str = os.getenv(
        "PASSWORD_HASH_ALGORITHM", "sha256_crypt"
    )  # Algorithm for password hashing

    # Face recognition settings
    FACE_DETECTION_MODEL: str = "hog"  # Options: "hog", "cnn"
    TOLERANCE: float = 0.6  # Lower values mean stricter matching

    # in STRICT_MODE, both face and username-password should be verified
    STRICT_MODE: bool = True

    # Server settings
    LISTEN_HOST: str = os.getenv("LISTEN_HOST", "0.0.0.0")
    LISTEN_PORT: int = int(os.getenv("LISTEN_PORT", "8000"))

    # Allowed origins for CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",  # Default Vue dev server
        "http://localhost:8080",  # Alternative Vue dev server
        "https://localhost",
        "https://localhost:3000",
        "https://localhost:8080",
    ]

    # class Config:
    #     """Pydantic configuration class to define env file settings."""

    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
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
