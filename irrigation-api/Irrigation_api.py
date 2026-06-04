from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, field_validator, Field
import re
import os
from mangum import Mangum
from datetime import datetime
from pydantic_core import PydanticCustomError
from database import engine, Base, SessionLocal
from users import register_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Irrigation API")
handler = Mangum(app)

API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY", "КОЙ ПОЛИВА И КОГА")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verifiy_api_key(header_key: str = Security(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong api key")
    return header_key


class UserRegister(BaseModel):
    username: str = Field(...)
    password: str = Field(..., min_length=5)

    @field_validator('username', mode='before')
    def validate_username(cls, v):
        if not isinstance(v, str):
            raise PydanticCustomError('Потребителското име трябва да е текст')

        username_clean = v.strip()

        if not username_clean:
            raise PydanticCustomError('empty_error', 'Потребителското неможе да е празно')
        if len(username_clean) < 3:
            raise PydanticCustomError('length_error', 'Потребителското име трябва да има поне 3 символа')
        if not v.strip():
            raise PydanticCustomError('value_error', 'Полето не може да бъде празно или да съдържа само интервали!')
        if not re.match(r'^[a-zA-Z0-9_а-яА-Я]+$', username_clean):
            raise PydanticCustomError('value_error',
                                      "Потребителското име може да съдържа само букви цифри и долни черти")
        return username_clean

    @field_validator('password')
    def validate_password(cls, v):
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


@app.post("/api/v1/zones/{zone_id}/toggle")
def toggle(zone_id: int, token: str = Depends(verifiy_api_key)):
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


@app.post("/api/v1/telemetry/")
def receive_telemetry(data: SensorData, token: str = Depends(verifiy_api_key)):
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "data is received", "telemetry": data}


@app.post("/api/v1/register")
def register_user_main(user_data: UserRegister):
    return register_user(user_data.username, user_data.password)


@app.post("/api/v1/login")
def login_user(user_data: UserRegister):
    return login_user(user_data.username , user_data.password)
