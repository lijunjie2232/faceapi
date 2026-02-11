"""
SQLデータベース用データベース初期化モジュール。

このモジュールは顔認識システム用のTortoise ORMを使用して
SQLデータベースの初期化とセットアップを処理します。
"""

from aerich import Command
from loguru import logger

from ..core import _CONFIG_

SUPPORT_SQL_BACKEND = [
    "sqlite",
    "mysql",
    "postgres",
    "psycopg",
    "asyncpg",
    "aiomysql",
    "asyncmy",
    "asyncodbc",
]

if _CONFIG_.SQL_BACKEND not in SUPPORT_SQL_BACKEND:
    raise ValueError(
        f"SQL_BACKENDは{SUPPORT_SQL_BACKEND}のいずれかである必要があります"
    )
if _CONFIG_.SQL_BACKEND == "sqlite":
    credentials_dict = {"file_path": _CONFIG_.SQL_DATABASE}
else:
    credentials_dict = {
        "host": _CONFIG_.SQL_HOST,
        "port": _CONFIG_.SQL_PORT,
        "user": _CONFIG_.SQL_USERNAME,
        "password": _CONFIG_.SQL_PASSWORD,
        "database": _CONFIG_.SQL_DATABASE,
    }

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": f"tortoise.backends.{_CONFIG_.SQL_BACKEND}",
            "credentials": credentials_dict,
        },
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "faceapi.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """SQLデータベースを初期化し、マイグレーションを実行"""
    async with Command(
        tortoise_config=TORTOISE_ORM,
    ) as command:
        try:
            await command.init_db(safe=True)
            logger.info("データベースを初期化しました")
        except FileExistsError:
            pass
        try:
            await command.migrate()
            logger.info("データベースマイグレーションが完了しました")
        except AttributeError:
            pass
        try:
            await command.upgrade(run_in_transaction=True)
            logger.info("データベースアップグレードが完了しました")
        except Exception:
            pass
        logger.debug(await command.history())
