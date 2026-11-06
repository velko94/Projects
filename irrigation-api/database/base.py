from abc import ABC, abstractmethod

class BaseUserRepository(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str):
        pass

    @abstractmethod
    def create_user(self, username: str, hashed_pwd: str):
        pass

class BaseZoneRepository(ABC):
    @abstractmethod
    def get_all_zones(self) -> dict:
        pass

    @abstractmethod
    def toggle_zone(self, zone_id: int, event_time: str) -> dict:
        pass

    @abstractmethod
    def add_zone(self, name: str) -> dict:
        pass

    @abstractmethod
    def delete_zone(self, zone_id: int) -> bool:
        pass