"""
Core module for the Face Recognition System.

This module initializes the configuration and logger for the application.
It loads the configuration settings and makes them available throughout
the application via the _CONFIG_ object.
"""

from loguru import logger

from .config import Config

_CONFIG_ = Config()

logger.info("Config Loaded")
logger.info(_CONFIG_)

__ALL__ = [
    "_CONFIG_",
]
