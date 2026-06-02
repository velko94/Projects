from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from database import SessionLocal,User
from security import get_password_encode

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


# def register_user(user_data.regi):
#     status = check_pwd(user_data.username,user_data.password)
#     if status == "Wrong password":
#         raise HTTPException(status_code=401, detail="Грешно подадена парола")
#     if status == "user already exists":
#
#     else:
#         create_user()
#     return {"status":"success","message":f"Потребител {user_data.username} е регистриран успешно!"}