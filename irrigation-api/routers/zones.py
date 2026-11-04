from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime

import database.factory
from config import API_KEY, API_KEY_NAME
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from database.factory import get_zone_repository

router = APIRouter(prefix="/api/v1", tags=["Zones"])
limiter = Limiter(key_func=get_remote_address)
from security import verify_jwt_token

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(header_key: str = Depends(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong api key")
    return header_key


class SensorData(BaseModel):
    temperature: float
    humidity: float

@router.get("/zones")
def check_zones():
    repo = get_zone_repository()
    return repo.get_all_zones()

@router.post("/zones/{zone_id}/toggle", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("5/minute")
async def toggle(request: Request, zone_id: int):
    event_time = datetime.now().strftime("%Y-%m-%d-%H:%M")
    repo = database.factory.get_zone_repository()
    zone = repo.toggle_zone(zone_id, event_time)
    if not zone:
        raise HTTPException(status_code=404, detail="No such zone")
    return {"message": f"Zone{zone_id} toggled successfully", "zone": zone}

@router.post("/telemetry/", dependencies=[Depends(verify_api_key)])
def receive_telemetry(data: SensorData):
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "data is received", "telemetry": data}
