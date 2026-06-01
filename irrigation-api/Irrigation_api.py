from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import os
from mangum import Mangum
from datetime import datetime
from database import engine, Base
from security import get_password_encode, check_pwd

get_password_encode()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Irrigation API")
handler = Mangum(app)

API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY", "кой полива и кога")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verifiy_api_key(header_key: str = Security(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong api key")
    return header_key


class UserRegister(BaseModel):
    username: str


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


@app.post("/api/v1/telemetry")
def receive_telemetry(data: SensorData, token: str = Depends(verifiy_api_key)):
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "data is received", "telemetry": data}


@app.post("api/v1/register/")
def register_user(username_input:str):
    status = check_pwd(username_input)
    if status == "Wrong password":
        raise HTTPException(status_code=401, detail="Грешно подадена парола")
    if status == "user already exists":
        raise HTTPException(status_code=400, detail="Този потребител вече существува")
    return {"status":"success","message":f"Потребител {username_input} е регистриран успешно!"}
