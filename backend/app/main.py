"""Main application module for Face Recognition System API.

This module initializes the FastAPI application, sets up the lifespan events,
registers middleware, and includes all API routes for the face recognition system.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .core import _CONFIG_
from .db import TORTOISE_ORM, init_milvus, init_sql
from .routes import admin, face, user


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan event handler for startup and shutdown events"""
    # Startup events
    await init_milvus()
    await init_sql()
    yield
    # Shutdown events (if any)


app = FastAPI(
    title=_CONFIG_.PROJECT_NAME,
    description="API for face recognition system with user management",
    version="0.1.0",
    lifespan=lifespan,
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CONFIG_.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "Face Recognition System API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routes using settings for prefix
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
