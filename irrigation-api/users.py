from fastapi import HTTPException
from security import get_password_encode, check_pwd, create_access_token
from database.factory import user_db


def register_user(username_input: str, raw_password: str):
    existing_user = user_db.get_user_by_username(username_input)
    if existing_user:
        raise HTTPException(status_code=400, detail="Този потребител вече съществува")

    hashed_string = get_password_encode(raw_password)
    user_db.create_user(username_input, hashed_string)
    return {"status": "success", "message": f"Потребител {username_input} е регистриран успешно"}


def login_user(username_input: str, raw_password: str):
    user_record = user_db.get_user_by_username(username_input)
    if not user_record:
        raise HTTPException(status_code=400, detail="Грешно потребителско име или парола")
    hashed_password_from_db = user_record[1]

    if not check_pwd(raw_password, hashed_password_from_db):
        raise HTTPException(status_code=400, detail="Грешна парола")
    access_token = create_access_token(data={"sub": username_input})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "status": "success",
        "message": f"Добре дошъл,{username_input}"
    }
