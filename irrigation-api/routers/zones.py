from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from config import API_KEY, API_KEY_NAME
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
router = APIRouter(prefix="/api/v1", tags=["Zones"])
limiter = Limiter(key_func=get_remote_address)
from security import verify_jwt_token

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(header_key: str = Depends(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong api key")
    return header_key

Zones_db = {
    1: {"name": "Домати и пипер", "status": "off", "last_watered": "Never"},
    3: {"name": "Краставици и тиквички", "status": "off", "last_watered": "Never"},
    4: {"name": "Ягоди", "status": "off", "last_watered": "Never"},
    5: {"name": "Дръвчета", "status": "off", "last_watered": "Never"}
}

class SensorData(BaseModel):
    temperature: float
    humidity: float

@router.get("/zones")
def check_zones():
    return Zones_db

@router.post("/zones/{zone_id}/toggle", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("5/minute")
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

@router.post("/telemetry/", dependencies=[Depends(verify_api_key)])
def receive_telemetry(data: SensorData):
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "data is received", "telemetry": data}
