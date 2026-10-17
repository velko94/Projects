import os
import bcrypt
from datetime import datetime, timedelta,timezone
import jwt
from fastapi import HTTPException, Security
from fastapi.security import  HTTPBearer, HTTPAuthorizationCredentials

def get_password_encode(raw_password: str):
    pwd_bytes = raw_password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed


def get_password_decode(hashed):
    decode_pwd = hashed.decode('utf-8')
    return decode_pwd  # - returns the decoded password


def check_pwd(raw_password: str, hashed_pwd_from_db: str):
    hex_str = str(hashed_pwd_from_db)[2:]
    hashed_clean = bytes.fromhex(hex_str).decode('utf-8')
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_clean.encode('utf-8'))


SECRET_KEY = os.getenv("JWT_SECRET", "СУПЕР_ТАЕН_КЛЮЧ_ЗА_ПОЛИВАНЕ")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

security_bearer = HTTPBearer()

def create_access_token(data: dict) -> str:
    """Генерира JWT токен"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)):
    """Проверява Bearer токена от Header-а"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")