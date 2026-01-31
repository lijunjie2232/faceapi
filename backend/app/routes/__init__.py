"""
Routes module for the Face Recognition System.

This module contains the API route definitions for the application,
organizing endpoints into logical groups such as admin, face recognition,
and user management.
"""

from .admin import router as admin
from .face import router as face
from .user import router as user

__ALL__ = [
    "admin",
    "face",
    "user",
]
