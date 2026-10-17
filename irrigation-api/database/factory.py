import os
from database.postgres_repo import PostgresUserRepository
from database.dynamo_repo import DynamoUserRepository


def get_user_repository():
    db_type = os.getenv("DB_TYPE", "postgres").lower()
    if db_type == "dynamo":
        return DynamoUserRepository()
    elif db_type == "postgres":
        return PostgresUserRepository()
    else:
        raise ValueError(f"Неподдържана базa данни: {db_type}")


user_db = get_user_repository()
