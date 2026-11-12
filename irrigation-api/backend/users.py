"""
Authentication Service module.
Handles business logic for user registration and login authentication,
integrating password hashing, database repositories, and JWT token issuance.
"""

from fastapi import HTTPException
from backend.security import get_password_encode, check_pwd, create_access_token
from database.factory import get_user_repository


def register_user(username_input: str, raw_password: str):
    """Registers a new user after verifying that the username is not already taken."""
    existing_user = get_user_repository().get_user_by_username(username_input)
    if existing_user:
        raise HTTPException(status_code=400, detail="Wrong username or password ")

    hashed_string = get_password_encode(raw_password)
    get_user_repository().create_user(username_input, hashed_string)
    return {"status": "success", "message": f"User '{username_input}' registered successfully!"}


def login_user(username_input: str, raw_password: str):
    """Authenticates a user by validating their credentials and generating a JWT access token."""
    user_record = get_user_repository().get_user_by_username(username_input)
    if not user_record:
        raise HTTPException(status_code=400, detail="Invalid username or password!")

    hashed_password_from_db = user_record[1]

    if not check_pwd(raw_password, hashed_password_from_db):
        raise HTTPException(status_code=400, detail="Invalid username or password!")

    access_token = create_access_token(data={"sub": username_input})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "status": "success",
        "message": f"Welcome back, {username_input}!"
    }