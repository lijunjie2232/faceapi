"""
Password utility module for encrypting and comparing passwords securely.
"""

from typing import Union

from passlib.context import CryptContext

# Configure the password hashing context to use sha256_crypt
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using sha256_crypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password as a string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if the passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def is_valid_password(password: str, min_length: int = 8) -> bool:
    """
    Check if a password meets basic validation requirements.

    Args:
        password: The password to validate
        min_length: Minimum required length (default: 8)

    Returns:
        True if the password is valid, False otherwise
    """
    if len(password) < min_length:
        return False

    # Check if password contains at least one uppercase, lowercase, digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    return has_upper and has_lower and has_digit


if __name__ == "__main__":
    # Example usage
    password = "MySecurePassword123"

    print(f"Original password: {password}")

    # Hash the password
    hashed = hash_password(password)
    print(f"Hashed password: {hashed}")

    # Verify the password
    is_correct = verify_password(password, hashed)
    print(f"Password verification result: {is_correct}")

    # Try with wrong password
    is_wrong = verify_password("WrongPassword", hashed)
    print(f"Wrong password verification result: {is_wrong}")
