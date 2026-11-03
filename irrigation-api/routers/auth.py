from fastapi import APIRouter, Request, status
from pydantic import BaseModel, field_validator, Field
import re
from pydantic_core import PydanticCustomError
from users import register_user, login_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

class UserRegister(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    @field_validator('username')
    def validate_username(cls, v):
        if not isinstance(v, str):
            raise PydanticCustomError('input_error', 'Потребителското име трябва да е текст')
        username_clean = v.strip()
        if not username_clean:
            raise PydanticCustomError('empty_error', 'Потребителското не може да е празно')
        if len(username_clean) < 3:
            raise PydanticCustomError('length_error', 'Потребителското име трябва да има поне 3 символа')
        if not re.match(r'^[a-zA-Z0-9_\u0400-\u04FF]+$', username_clean):
            raise PydanticCustomError('value_error', "Потребителското име може да съдържа само букви цифри и долни черти")
        return username_clean

    @field_validator('password')
    def validate_password(cls, v):
        pwd_clean = v.strip()
        if len(pwd_clean) < 5:
            raise PydanticCustomError('length_error', 'Паролата трябва да е поне 5 символа')
        return pwd_clean

@router.post("/register")
def register_user_endpoint(user_data: UserRegister):
    return register_user(user_data.username, user_data.password)

@router.post("/login")
@limiter.limit("5/minute")
def login_endpoint(request: Request, user_data: UserRegister):
    return login_user(user_data.username, user_data.password)