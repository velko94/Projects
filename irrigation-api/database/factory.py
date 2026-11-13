"""
Database Factory module.
Dynamically determines and instantiates the appropriate repository (PostgreSQL or DynamoDB)
based on environment variables and deployment context (AWS Lambda vs local).
"""

import os
from backend.config import IS_AWS_LAMBDA
from database.base import BaseUserRepository, BaseZoneRepository


def get_db_type() -> str:
    """Determines which database backend to use based on environment configuration."""
    db_type = os.getenv("DB_TYPE", "").lower()
    if db_type in ["postgres", "dynamo"]:
        return db_type

    # Default to DynamoDB if running on AWS Lambda, otherwise fall back to PostgreSQL
    return "dynamo" if IS_AWS_LAMBDA else "postgres"


def get_user_repository() -> BaseUserRepository:
    """Factory method to instantiate and return the correct User repository implementation."""
    db_type = get_db_type()
    print(f"---- FACTORY: Initializing User Repository with DB_TYPE: {db_type} ----")

    if db_type == "postgres":
        try:
            from database.postgres_repo import PostgresUserRepository
            return PostgresUserRepository()
        except ImportError as e:
            raise RuntimeError("PostgreSQL repository selected, but required dependencies are missing.") from e
    elif db_type == "dynamo":
        from database.dynamo_repo import DynamoUserRepository
        return DynamoUserRepository()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def get_zone_repository() -> BaseZoneRepository:
    """Factory method to instantiate and return the correct Zone repository implementation."""
    db_type = get_db_type()
    print(f"---- FACTORY: Initializing Zone Repository with DB_TYPE: {db_type} ----")

    if db_type == "postgres":
        try:
            from database.postgres_repo import PostgresZoneRepository
            return PostgresZoneRepository()
        except ImportError as e:
            raise RuntimeError("PostgreSQL repository selected, but required dependencies are missing.") from e
    elif db_type == "dynamo":
        from database.dynamo_repo import DynamoZoneRepository
        return DynamoZoneRepository() # type: ignore
    else:
        raise ValueError(f"Unsupported database type: {db_type}")