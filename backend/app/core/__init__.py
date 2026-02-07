"""
顔認識システムのコアモジュール。

このモジュールはアプリケーションの設定とロガーを初期化します。
設定を読み込み、_CONFIG_オブジェクトを介してアプリケーション全体で
利用できるようにします。
"""

from loguru import logger

from .config import Config

_CONFIG_ = Config()

logger.info("Config Loaded")
logger.info(_CONFIG_)

__ALL__ = [
    "_CONFIG_",
]
