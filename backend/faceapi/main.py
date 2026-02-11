"""顔認識システムAPIのメインアプリケーションモジュール。

このモジュールはFastAPIアプリケーションを初期化し、ライフスパンイベントを設定し、
ミドルウェアを登録し、顔認識システムのすべてのAPIルートを含みます。
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import asyncio

from faceapi.core import _CONFIG_
from faceapi.db import TORTOISE_ORM, milvus_init, sql_init, create_init_account
from faceapi.routes import admin, face, user


@asynccontextmanager
async def lifespan(_: FastAPI):
    """起動およびシャットダウンイベントのライフスパンイベントハンドラ"""
    # 起動イベント
    await asyncio.gather(milvus_init(), sql_init())
    await create_init_account()
    yield
    # シャットダウンイベント（もしあれば）


app = FastAPI(
    title=_CONFIG_.PROJECT_NAME,
    description="ユーザー管理機能付き顔認識システムのAPI",
    version="0.1.0",
    lifespan=lifespan,
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

# CORSミドルウェアを追加r
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CONFIG_.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ヘルスチェック用のルートエンドポイント"""
    return {"message": "Face Recognition System API"}


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


# 設定を使用してAPIルートを含める
app.include_router(
    user,
    prefix=_CONFIG_.API_V1_STR,
)
app.include_router(
    face,
    prefix=_CONFIG_.API_V1_STR,
)
app.include_router(
    admin,
    prefix=_CONFIG_.API_V1_STR,
)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=_CONFIG_.LISTEN_HOST,
        port=_CONFIG_.LISTEN_PORT,
    )
