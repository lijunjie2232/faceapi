"""
User model module for the Face Recognition System.

This module defines the database model for user accounts,
including fields for authentication, profile information, and metadata.
"""

from tortoise import fields
from tortoise.models import Model


class UserModel(Model):
    """
    Database model for user accounts.

    This model stores user account information including authentication details,
    profile information, and metadata about the account status and creation time.
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(max_length=200, unique=True)
    full_name = fields.CharField(max_length=200, null=True)
    hashed_password = fields.CharField(max_length=200)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    head_pic = fields.TextField(null=True)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        """Meta class to define table configuration."""

        table = "users"

    def __str__(self):
        return self.username
