"""
Database initialization module for SQL databases.

This module handles the initialization and setup of SQL databases
using Tortoise ORM for the face recognition system.
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
    raise ValueError(f"SQL_BACKEND must be one of {SUPPORT_SQL_BACKEND}")
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
            "models": ["aerich.models", "backend.app.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize the SQL database and run migrations"""
    async with Command(
        tortoise_config=TORTOISE_ORM,
    ) as command:
        try:
            await command.init_db(safe=True)
            logger.info("Database initialized")
        except FileExistsError:
            pass
        try:
            await command.migrate()
            logger.info("Database migration completed")
        except AttributeError:
            pass
        try:
            await command.upgrade(run_in_transaction=True)
            logger.info("Database upgrade completed")
        except Exception:
            pass
        logger.debug(await command.history())
