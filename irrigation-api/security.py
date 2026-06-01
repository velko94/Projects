import bcrypt

global pwd_bytes, hashed
from database import register_user


def get_password_encode():
    global pwd_bytes, hashed
    pwd_bytes = input("type yоur password: ", ).encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())


def get_password_decode():
    decode_pwd = hashed.decode('utf-8')
    return decode_pwd  # - returns the decoded password


def check_pwd(username_input: str):
    if bcrypt.checkpw(pwd_bytes, hashed):
        print("it matches")
        db_hash_str = get_password_decode()
        status = register_user(username_input, db_hash_str)
        return status
    else:
        print("Passwords don't match")
        return "Wrong password"
