"""
Authentication router handling user registration and login endpoints.
Includes strict Pydantic data validation for usernames and passwords,
along with Rate Limiting protection against brute-force attacks.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator, Field
import re
from pydantic_core import PydanticCustomError
from backend.users import register_user, login_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


class UserRegister(BaseModel):
    """
    Pydantic model for user registration and login payload validation.
    Enforces rules on username characters/length and password strength.
    """
    username: str = Field(...)
    password: str = Field(...)

    @field_validator('username')
    def validate_username(cls, v):
        """Validates username format, length, and allowed characters (supports Latin, Cyrillic, and numbers)."""
        if not isinstance(v, str):
            raise PydanticCustomError('input_error', 'Username must be a text string.')

        username_clean = v.strip()
        if not username_clean:
            raise PydanticCustomError('empty_error', 'Username cannot be empty.')

        if len(username_clean) < 3:
            raise PydanticCustomError('length_error', 'Username must be at least 3 characters long.')

        if not re.match(r'^[a-zA-Z0-9_\u0400-\u04FF]+$', username_clean):
            raise PydanticCustomError(
                'value_error',
                'Username can only contain letters, numbers, and underscores.'
            )
        return username_clean

    @field_validator('password')
    def validate_password(cls, v):
        """Validates password length and checks against a blacklist of common weak passwords."""
        pwd_clean = v.strip()

        if len(pwd_clean) < 8:
            raise PydanticCustomError('length_error', 'Password must be at least 8 characters long.')

        common_weak_passwords = ["string", "123456", "password", "admin", "12345678"]
        if pwd_clean.lower() in common_weak_passwords:
            raise PydanticCustomError('weak_password', 'This password is too weak and not allowed.')

        return pwd_clean


@router.post("/register")
@limiter.limit("5/minute")
def register_user_endpoint(request: Request, user_data: UserRegister):
    """
    Endpoint for registering a new user.
    Protected by a rate limit of 5 requests per minute per IP address.
    """
    return register_user(user_data.username, user_data.password)


@router.post("/login")
@limiter.limit("5/minute")
def login_endpoint(request: Request, user_data: UserRegister):
    """
    Endpoint for user authentication (login).
    Protected by a rate limit of 5 requests per minute per IP address.
    """
    return login_user(user_data.username, user_data.password)