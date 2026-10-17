from sqlalchemy import text
from database.connection import SessionLocal, User
from database.base import BaseUserRepository


class PostgresUserRepository(BaseUserRepository):
    def get_user_by_username(self, username: str):
        db = SessionLocal()
        try:
            query = text("SELECT username, user_password FROM users WHERE username =:user ")
            return db.execute(query, {"user": username}).fetchone()
        finally:
            db.close()

    def create_user(self, username: str, hashed_pwd: str):
        db = SessionLocal()
        try:
            db_user = User(username=username, user_password=hashed_pwd)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        finally:
            db.close()
