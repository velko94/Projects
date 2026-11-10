"""
Authentication and Security module.
Handles password hashing and verification using bcrypt, JWT token generation
and validation, and API key header verification for secure endpoint access.
"""

import os
import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from backend.config import API_KEY, API_KEY_NAME

# API Key header security scheme
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_password_encode(raw_password: str) -> str:
    """Hashes a raw password using bcrypt and returns its hex representation."""
    pwd_bytes = raw_password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.hex()


def get_password_decode(hashed) -> str:
    """Decodes a bcrypt hashed password bytes object into a string."""
    decode_pwd = hashed.decode('utf-8')
    return decode_pwd


def check_pwd(raw_password: str, hex_from_db: str) -> bool:
    """Verifies a raw password against a stored hex-encoded bcrypt hash."""
    try:
        hashed_bytes = bytes.fromhex(hex_from_db)
        return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_bytes)
    except (ValueError, TypeError):
        return False


# JWT Configuration settings
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_irrigation_jwt_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Updated to a standard practical session window

security_bearer = HTTPBearer()


def create_access_token(data: dict) -> str:
    """Generates a JSON Web Token (JWT) containing the provided payload data."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> str:
    """Validates the Bearer JWT token from the authorization header and extracts the username."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")


def verify_api_key(header_key: str = Security(api_key_header)) -> str:
    """Validates the custom API key passed via the request header."""
    if not header_key or header_key.strip().lower() != API_KEY.strip().lower():
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return header_key