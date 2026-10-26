from fastapi import FastAPI, HTTPException, Security, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, field_validator, Field
import re
import os
from mangum import Mangum
from datetime import datetime
from pydantic_core import PydanticCustomError
from starlette.responses import JSONResponse
from database.connection import engine, Base
from users import register_user, login_user
from security import verify_jwt_token
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Irrigation API")
handler = Mangum(app)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY", "КОЙ ПОЛИВА И КОГА")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(header_key: str = Security(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong api key")
    return header_key


class UserRegister(BaseModel):
    username: str = Field(...)
    password: str = Field(..., min_length=5)

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
            raise PydanticCustomError('value_error',
                                      "Потребителското име може да съдържа само букви цифри и долни черти")
        return username_clean

    @field_validator('password')
    def validate_password(cls, v):  # v stands for value provided by the customer
        pwd_clean = v.strip()
        if len(pwd_clean) < 5:
            raise PydanticCustomError('length_error', 'Паролата трябва да е поне 5 символа')
        return pwd_clean


Zones_db = {
    1: {"name": "Домати и пипер", "status": "off", "last_watered": "Never"},
    3: {"name": "Краставици и тиквички", "status": "off", "last_watered": "Never"},
    4: {"name": "Ягоди", "status": "off", "last_watered": "Never"},
    5: {"name": "Дръвчета", "status": "off", "last_watered": "Never"}
}


class SensorData(BaseModel):
    temperature: float
    humidity: float


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    cleaned_errors = []
    for err in exc.errors():
        err_dict = dict(err)
        err_dict.pop("input", None)  # Премахва input полето от отговора
        cleaned_errors.append(err_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": cleaned_errors},
    )


@app.post("/api/v1/zones/{zone_id}/toggle", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def toggle(request: Request, zone_id: int):
    event_time = datetime.now()
    if zone_id not in Zones_db:
        raise HTTPException(status_code=404, detail="No such zone")
    zone = Zones_db[zone_id]
    if zone["status"] == "off":
        zone["status"] = "on"
        zone["last_watered"] = event_time.strftime("%Y-%m-%d-%H-%M")
    else:
        zone["status"] = "off"
    return {"message": f"Zone{zone_id} toggled successfully", "zone": zone}


@app.get("/api/v1/zones")
def check_zones():
    return Zones_db


@app.post("/api/v1/telemetry/", dependencies=[Depends(verify_api_key)])
def receive_telemetry(data: SensorData):
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "data is received", "telemetry": data}


@app.post("/api/v1/register")
def register_user_main(user_data: UserRegister):
    return register_user(user_data.username, user_data.password)


@app.post("/api/v1/login")
@limiter.limit("5/minute")
def login(request: Request, user_data: UserRegister):
    return login_user(user_data.username, user_data.password)


@app.get("/api/v1/users/me")
def get_current_user_info(current_user: str = Depends(verify_jwt_token)):
    return {
        "status": "success",
        "username": current_user,
        "message": f"Успешен достъп с JWT токен за {current_user}!"
    }
