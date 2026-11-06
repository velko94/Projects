from fastapi import HTTPException

from database.base import BaseUserRepository, BaseZoneRepository
from sqlalchemy import Column, Integer, String, text
from database.connection import Base, SessionLocal, User, engine


def init_db():  # creates the tables if they don't exist
    Base.metadata.create_all(bind=engine)


class PostgresUserRepository(BaseUserRepository):
    def get_user_by_username(self, username: str):
        db = SessionLocal()
        try:
            query = text("SELECT username, user_password FROM users WHERE username = :user")
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

    def add_zone(self, name: str) -> dict:
        db = SessionLocal()
        try:
            # Проверка за дубликат по име преди добавяне
            existing_zone = db.query(ZoneModel).filter(ZoneModel.name == name).first()
            if existing_zone:
                raise HTTPException(status_code=400, detail="Зона с това име вече съществува!")

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
