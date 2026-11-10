<<<<<<< HEAD
"""
PostgreSQL repository implementation using SQLAlchemy.
Handles database initialization, user persistence, and irrigation zone CRUD operations.
"""

from fastapi import HTTPException
from database.base import BaseUserRepository, BaseZoneRepository
from sqlalchemy import Column, Integer, String, text
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
=======
from sqlalchemy import text
from database.connection import SessionLocal, User
from database.base import BaseUserRepository


class PostgresUserRepository(BaseUserRepository):
    def get_user_by_username(self, username: str):
        db = SessionLocal()
        try:
            query = text("SELECT username, user_password FROM users WHERE username =:user ")
>>>>>>> origin/master
            return db.execute(query, {"user": username}).fetchone()
        finally:
            db.close()

    def create_user(self, username: str, hashed_pwd: str):
<<<<<<< HEAD
        """Creates and persists a new user with a hashed password."""
=======
>>>>>>> origin/master
        db = SessionLocal()
        try:
            db_user = User(username=username, user_password=hashed_pwd)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        finally:
            db.close()
<<<<<<< HEAD


class ZoneModel(Base):
    """SQLAlchemy model representing an irrigation zone in PostgreSQL."""
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="off")
    last_watered = Column(String, default="Never")


class PostgresZoneRepository(BaseZoneRepository):
    """Repository handling irrigation zone management and telemetry state in PostgreSQL."""

    def get_all_zones(self) -> dict:
        """Retrieves all irrigation zones formatted as a dictionary mapped by their IDs."""
        db = SessionLocal()
        try:
            zones = db.query(ZoneModel).all()
            return {
                z.id: {"name": z.name, "status": z.status, "last_watered": z.last_watered}
                for z in zones
            }
        finally:
            db.close()

    def toggle_zone(self, zone_id: int, event_time: str) -> dict:
        """
        Toggles a zone's operational state ('on'/'off'). 
        If turning 'on', records the current timestamp.
        """
        db = SessionLocal()
        try:
            zone = db.query(ZoneModel).filter(ZoneModel.id == zone_id).first()
            if not zone:
                return None

            if zone.status == "off":
                zone.status = "on"
                zone.last_watered = event_time
            else:
                zone.status = "off"

            db.commit()
            db.refresh(zone)
            return {"name": zone.name, "status": zone.status, "last_watered": zone.last_watered}
        finally:
            db.close()

    def add_zone(self, name: str) -> dict:
        """Adds a new irrigation zone, checking for duplicate names first."""
        db = SessionLocal()
        try:
            existing_zone = db.query(ZoneModel).filter(ZoneModel.name == name).first()
            if existing_zone:
                raise HTTPException(status_code=400, detail="A zone with this name already exists!")

            new_zone = ZoneModel(name=name, status="off", last_watered="Never")
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

    def delete_zone(self, zone_id: int) -> bool:
        """Deletes an irrigation zone by its ID. Returns True if successful, False otherwise."""
        db = SessionLocal()
        try:
            zone = db.query(ZoneModel).filter(ZoneModel.id == zone_id).first()
            if not zone:
                return False
            db.delete(zone)
            db.commit()
            return True
        finally:
            db.close()
=======
>>>>>>> origin/master
