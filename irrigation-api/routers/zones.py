"""
Zones router handling irrigation zone management (CRUD), manual toggling,
sensor telemetry ingestion, and security enforcement (JWT tokens & API Keys).
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
import database.factory
from backend.config import API_KEY, API_KEY_NAME
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from database.factory import get_zone_repository
from backend.security import verify_jwt_token

router = APIRouter(prefix="/api/v1", tags=["Zones"])
limiter = Limiter(key_func=get_remote_address)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(header_key: str = Depends(api_key_header)):
    """Validates the incoming API key header for IoT sensor telemetry requests."""
    if header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return header_key


class SensorData(BaseModel):
    """Pydantic model for incoming IoT sensor telemetry data."""
    temperature: float
    humidity: float


class ZoneCreate(BaseModel):
    """Pydantic model for creating a new irrigation zone."""
    name: str


@router.get("/zones")
def check_zones():
    """Retrieves a dictionary from DB of all configured irrigation zones and their statuses."""
    repo = get_zone_repository()
    return repo.get_all_zones()


@router.post("/zones", dependencies=[Depends(verify_jwt_token)])
def create_zone(zone_data: ZoneCreate):
    """Creates a new irrigation zone. Requires an active user JWT token."""
    repo = get_zone_repository()
    return repo.add_zone(zone_data.name)


@router.delete("/zones/{zone_id}", dependencies=[Depends(verify_jwt_token)])
def delete_zone(zone_id: int):
    """Deletes an irrigation zone by its ID. Requires an active user JWT token."""
    repo = get_zone_repository()
    success = repo.delete_zone(zone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Zone not found.")
    return {"message": f"Zone {zone_id} deleted successfully."}


@router.post("/zones/{zone_id}/toggle", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("5/minute")
async def toggle(request: Request, zone_id: int):
    """
    Toggles an irrigation zone state (on/off) and updates the last watered timestamp.
    Protected by rate limiting (max 5 requests/minute) and JWT authentication.
    """
    event_time = datetime.now().strftime("%Y-%m-%d-%H:%M")
    repo = database.factory.get_zone_repository()
    zone = repo.toggle_zone(zone_id, event_time)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found.")
    return {"message": f"Zone {zone_id} toggled successfully.", "zone": zone}


@router.post("/telemetry/", dependencies=[Depends(verify_api_key)])
def receive_telemetry(data: SensorData):
    """
    Endpoint for IoT hardware sensors to push environmental telemetry data.
    Secured via a pre-shared API Key header. Evaluates soil moisture levels.
    """
    if data.humidity < 30:
        return {"status": "success", "msg": "Soil is dry, consider watering!", "telemetry": data}
    else:
        return {"status": "success", "msg": "Data received successfully.", "telemetry": data}