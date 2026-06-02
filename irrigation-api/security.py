import os
import bcrypt

global pwd_bytes, hashed


def get_password_encode(raw_password: str):
    api_key_string = os.getenv("IRRIGATION_API_KEY", "КОЙ ПОЛИВА И КОГА")
    pwd_bytes = raw_password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed


def get_password_decode():
    decode_pwd = hashed.decode('utf-8')
    return decode_pwd  # - returns the decoded password


def check_pwd(raw_password: str, hashed_pwd_from_db: str):
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_pwd_from_db.encode('utf-8'))
