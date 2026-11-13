"""
PostgreSQL repository implementation using SQLAlchemy.
Handles database initialization, user persistence, and irrigation zone CRUD operations.
"""

from fastapi import HTTPException
from database.base import BaseUserRepository, BaseZoneRepository
from sqlalchemy import Column, Integer, String, text,Float
from database.connection import Base, SessionLocal, User, engine


def init_db():
    """Creates all database tables defined in metadata if they do not already exist."""
    Base.metadata.create_all(bind=engine)


class PostgresUserRepository(BaseUserRepository):
    """Repository handling user data operations against PostgreSQL."""

    def get_user_by_username(self, username: str):
        """Retrieves a user record by username using raw SQL text query."""
        db = SessionLocal()
        try:
            query = text("SELECT username, user_password FROM users WHERE username = :user")
            return db.execute(query, {"user": username}).fetchone()
        finally:
            db.close()

    def create_user(self, username: str, hashed_pwd: str):
        """Creates and persists a new user with a hashed password."""
        db = SessionLocal()
        try:
            db_user = User(username=username, user_password=hashed_pwd)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        finally:
            db.close()


class ZoneModel(Base):
    """SQLAlchemy model representing an irrigation zone in PostgreSQL."""
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    status = Column(String, default="off")
    last_watered = Column(String, default="Never")
    last_watered_duration = Column(String,default="00:00")
    started_at = Column(Float, nullable=True)

class PostgresZoneRepository(BaseZoneRepository):
    """Repository handling irrigation zone management and telemetry state in PostgreSQL."""

    def get_all_zones(self) -> dict:
        """Retrieves all zones (fallback)."""
        db = SessionLocal()
        try:
            zones = db.query(ZoneModel).all()
            return {
                z.id: {"name": z.name, "status": z.status, "last_watered": z.last_watered}
                for z in zones
            }
        finally:
            db.close()

    def get_zones_by_user(self, owner: str) -> dict:
        """Retrieves irrigation zones strictly for a specific user."""
        db = SessionLocal()
        try:
            zones = db.query(ZoneModel).filter(ZoneModel.owner == owner).all()
            return {
                z.id: {
                    "name": z.name,
                    "status": z.status,
                    "last_watered": z.last_watered,
                    "last_watered_duration": z.last_watered_duration
                }
                for z in zones
            }
        finally:
            db.close()

    def toggle_zone(self, zone_id: int, event_time: str, owner: str = None) -> dict:
        """Toggles a zone and automatically calculates running duration based on timestamps."""
        import time
        db = SessionLocal()
        try:
            query = db.query(ZoneModel).filter(ZoneModel.id == zone_id)
            if owner:
                query = query.filter(ZoneModel.owner == owner)
            zone = query.first()

            if not zone:
                return None

            current_time = time.time()

            if zone.status == "off":
                zone.status = "on"
                zone.started_at = current_time  # save when started
            else:
                zone.status = "off"
                zone.last_watered = event_time

                # count the time it worked
                if zone.started_at:
                    elapsed_seconds = int(current_time - zone.started_at)
                    hours = elapsed_seconds // 3600
                    minutes = (elapsed_seconds % 3600) // 60
                    seconds = elapsed_seconds % 60

                    if zone.started_at:
                        elapsed_seconds = int(current_time - zone.started_at)
                        days = elapsed_seconds // 86400
                        hours = (elapsed_seconds % 86400) // 3600
                        minutes = (elapsed_seconds % 3600) // 60
                        seconds = elapsed_seconds % 60
                        if days > 0:
                            zone.last_watered_duration = f"{days}d {hours}h {minutes}m"
                        elif hours > 0:
                            zone.last_watered_duration = f"{hours}h {minutes}m"
                        elif minutes > 0:
                            zone.last_watered_duration = f"{minutes}m {seconds}s"
                        else:
                            zone.last_watered_duration = f"{seconds}s"
                else:
                    zone.last_watered_duration = "N/A"
                zone.started_at = None  # clears the started at

            db.commit()
            db.refresh(zone)
            return {
                "name": zone.name,
                "status": zone.status,
                "last_watered": zone.last_watered,
                "last_watered_duration": zone.last_watered_duration
            }
        finally:
            db.close()



    def add_zone(self, name: str, owner: str = "default_user") -> dict:
        """Adds a new irrigation zone linked to the active user."""
        db = SessionLocal()
        try:
            user_zones_count = db.query(ZoneModel).filter(ZoneModel.owner == owner).count()
            if user_zones_count >= 20:
                raise HTTPException(status_code=400, detail="Maximum limit of 20 zones reached for this account.")
            existing_zone = db.query(ZoneModel).filter(ZoneModel.name == name, ZoneModel.owner == owner).first()
            if existing_zone:
                raise HTTPException(status_code=400, detail="A zone with this name already exists!")

            # 3. Създаване на новата зона
            new_zone = ZoneModel(name=name, owner=owner, status="off", last_watered="Never")
            db.add(new_zone)
            db.commit()
            db.refresh(new_zone)
            return {
                "id": new_zone.id,
                "name": new_zone.name,
                "status": new_zone.status,
                "last_watered": new_zone.last_watered
            }
        finally:
            db.close()

    def delete_zone(self, zone_id: int, owner: str = None) -> bool:
        """Deletes an irrigation zone by its ID and owner."""
        db = SessionLocal()
        try:
            query = db.query(ZoneModel).filter(ZoneModel.id == zone_id)
            if owner:
                query = query.filter(ZoneModel.owner == owner)
            zone = query.first()

            if not zone:
                return False
            db.delete(zone)
            db.commit()
            return True
        finally:
            db.close()