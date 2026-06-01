import os
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv


load_dotenv()
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# SQL ALCHEMY infra
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# sqlaclchemy scheme for postgres
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    user_password = Column(String, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db  # -gives session ot the user
    finally:
        db.close()


def create_user(db: Session, username_input: str, hashed_pwd: str):
    db_user = User(username=username_input, user_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def register_user(username_input: str, hashed_pwd: str):
    db = SessionLocal()
    try:
        query = text("SELECT * FROM users WHERE username= :user")
        result = db.execute(query, {"user": username_input}).fetchone()
        if result:
            return "user already exists"
        else:
            create_user(db, username_input,hashed_pwd)
            return "User created"
    finally:
       db.close()
