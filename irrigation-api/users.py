from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal, User
from security import get_password_encode, check_pwd


def create_user(db: Session, username_input: str, hashed_pwd: str):
    db_user = User(username=username_input, user_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def register_user(username_input: str, raw_password: str):
    db = SessionLocal()
    try:
        query = text("SELECT * FROM users WHERE username= :user")
        result = db.execute(query, {"user": username_input}).fetchone()
        if result:
            raise HTTPException(status_code=400, detail="Този потребител вече существува")
        else:
            hashed_string = get_password_encode(raw_password)
            create_user(db, username_input, hashed_string)
            db.commit()
            return {"status": "success", "message": f"Потребител {username_input} е регистриран успешно!"}
    finally:
        db.close()


def login_user(username_input: str, raw_password: str):
    db = SessionLocal()
    try:

        query = text("SELECT username, user_password FROM users WHERE username = :user")
        user_record = db.execute(query, {"user": username_input}).fetchone()

        if not user_record:
            raise HTTPException(status_code=400, detail="Грешно потребителско име или парола")
        hashed_password_from_db = user_record[1]

        if not check_pwd(raw_password, hashed_password_from_db):
            raise HTTPException(status_code=400, detail="Грешно потребителско име или парола")
        return {"status": "success", "message": f"Добре дошъл, {username_input}"}

    finally:
        db.close()
