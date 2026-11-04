from database.base import BaseUserRepository, BaseZoneRepository
from sqlalchemy import Column, Integer, String, text
from database.connection import Base, SessionLocal, User


class PostgresUserRepository(BaseUserRepository):
    def get_user_by_username(self, username: str):
        db = SessionLocal()
        try:
            query = text("SELECT username, user_password FROM users WHERE username =:user ")
            return db.execute(query, {"user": username}).fetchone()
        finally:
            db.close()

    def create_user(self, username: str, hashed_pwd: str):
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
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="off")
    last_watered = Column(String, default="Never")


class PostgresZoneRepository(BaseZoneRepository):
    def get_all_zones(self) -> dict:
        db = SessionLocal()
        try:
            zones = db.query(ZoneModel).all()
            # Превръщаме в речник с ключ ID-то, за да съвпада със старото поведение на app.js
            return {
                z.id: {"name": z.name, "status": z.status, "last_watered": z.last_watered}
                for z in zones
            }
        finally:
            db.close()

    def toggle_zone(self, zone_id: int, event_time: str) -> dict:
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
