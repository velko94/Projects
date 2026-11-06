import os
from config import IS_AWS_LAMBDA
from database.base import BaseUserRepository, BaseZoneRepository


# function to decide what hte db is
def get_db_type() -> str:
    # check if DB_TYPE is in env (postgres или dynamo)
    db_type = os.getenv("DB_TYPE", "").lower()
    if db_type in ["postgres", "dynamo"]:
        return db_type

    # defualts if not specific db type is set to is lambda or postgres
    return "dynamo" if IS_AWS_LAMBDA else "postgres"


def get_user_repository() -> BaseUserRepository:
    db_type = get_db_type()
    print(f"---- FACTORY: Initializing User Repository with DB_TYPE: {db_type} ----")

    if db_type == "postgres":
        try:
            from database.postgres_repo import PostgresUserRepository
            return PostgresUserRepository()
        except ImportError as e:
            raise RuntimeError("Postgres репо-то е избрано, но липсват зависимости.") from e
    elif db_type == "dynamo":
        from database.dynamo_repo import DynamoUserRepository
        return DynamoUserRepository()
    else:
        raise ValueError(f"Неподдържана база данни: {db_type}")


def get_zone_repository() -> BaseZoneRepository:
    db_type = get_db_type()
    print(f"---- FACTORY: Initializing Zone Repository with DB_TYPE: {db_type} ----")

    if db_type == "postgres":
        from database.postgres_repo import PostgresZoneRepository
        return PostgresZoneRepository()
    elif db_type == "dynamo":
        from database.dynamo_repo import DynamoZoneRepository
        return DynamoZoneRepository()
    else:
        raise ValueError(f"Неподдържана база данни: {db_type}")

