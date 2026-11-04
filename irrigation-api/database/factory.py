import os
from config import IS_AWS_LAMBDA
from database.dynamo_repo import DynamoUserRepository,DynamoZoneRepository
from database.postgres_repo import PostgresZoneRepository
from database.base import BaseZoneRepository


def get_user_repository():
    db_type = os.getenv("DB_TYPE", "dynamo").lower()
    print(f"---- DATABASE FACTORY INITIALIZING WITH DB_TYPE:{db_type} ----")
    if db_type == "dynamo":
        return DynamoUserRepository()
    elif db_type == "postgres":
        try:
            from database.postgres_repo import PostgresUserRepository
            return PostgresUserRepository()
        except ImportError as e:
            raise RuntimeError(
                "Postgres репо-то е избрано (DB_TYPE = postgres), "
                "но липсват SQLAlchemy или postgres_repo зависимости в средата"
            ) from e
    else:
        raise ValueError(f"Неподдържана базa данни: {db_type}")

def get_zone_repository() -> BaseZoneRepository:
    if IS_AWS_LAMBDA:
        return DynamoZoneRepository()
    else:
        return PostgresZoneRepository()