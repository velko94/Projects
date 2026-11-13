"""
Unit tests for authentication and JWT security logic:
1. Duplicate user registration prevention.
2. Independent login for different users sharing the same password.
3. JWT token generation, valid decoding, and expiration/invalid handling.
"""

import pytest
from fastapi import HTTPException
from routers.auth import register_user, login_user
from backend.security import create_access_token, verify_jwt_token
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta, datetime, timezone
import jwt


def test_duplicate_user_registration():
    """Test 1: Registering the same username twice must raise an HTTP 400 exception."""
    username = "ivan_irrigation"
    password = "SecurePassword123"

    # First registration should succeed
    resp1 = register_user(username, password)
    assert resp1["status"] == "success"

    # Second registration with the same username should fail with HTTP 400
    with pytest.raises(HTTPException) as exc_info:
        register_user(username, password)

    assert exc_info.value.status_code == 400
    assert "already taken" in exc_info.value.detail # type: ignore


def test_different_users_same_password():
    """Test 2: Two different users with the same password register and log in successfully independently."""
    passphrase = "SharedPassword999"
    user_a = "alice"
    user_b = "bob"

    # Register User A and B
    assert register_user(user_a, passphrase)["status"] == "success"
    assert register_user(user_b, passphrase)["status"] == "success"

    # Login and verify tokens are issued
    login_a = login_user(user_a, passphrase)
    assert login_a["status"] == "success"
    assert "access_token" in login_a

    login_b = login_user(user_b, passphrase)
    assert login_b["status"] == "success"
    assert "access_token" in login_b

    # Wrong password check
    with pytest.raises(HTTPException) as exc_info:
        login_user(user_a, "WrongPassword")
    assert exc_info.value.status_code == 400


def test_jwt_token_generation_and_verification():
    """Test 3: JWT tokens correctly encode the username and verify successfully."""
    username = "inspector_gadget"

    # Generate token using the security module helper
    token_str = create_access_token(data={"sub": username})
    assert isinstance(token_str, str)
    assert len(token_str) > 20

    # Mock the HTTPAuthorizationCredentials object expected by verify_jwt_token
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)

    # Verify the token and ensure it extracts the correct username
    extracted_username = verify_jwt_token(credentials)
    assert extracted_username == username


def test_jwt_token_expired_handling():
    """Test 4: An expired JWT token must be rejected with HTTP 401."""
    username = "expired_user"

    # Manually create a token that is already expired (expiration set in the past)
    expired_payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=15)
    }

    from backend.security import SECRET_KEY, ALGORITHM
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

    # Verification should raise HTTP 401 due to token expiration
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(credentials)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower() # type: ignore


def test_jwt_token_invalid_signature():
    """Test 5: A tampered or invalid JWT token must be rejected with HTTP 401."""
    # Create a token with a completely different secret key
    forged_payload = {"sub": "hacker"}
    forged_token = jwt.encode(forged_payload, "wrong_secret_key", algorithm="HS256")

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=forged_token)

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(credentials)

    assert exc_info.value.status_code == 401
    assert "validate" in exc_info.value.detail.lower() # type: ignore