<<<<<<< HEAD
"""
Abstract Repository Interfaces module.
Defines the base contracts (interfaces) for user and irrigation zone data operations,
ensuring strict decoupling and interchangeability between different database backends (PostgreSQL, DynamoDB).
"""

=======
>>>>>>> origin/master
from abc import ABC, abstractmethod


class BaseUserRepository(ABC):
<<<<<<< HEAD
    """Abstract base class defining the required contract for user data operations."""

    @abstractmethod
    def get_user_by_username(self, username: str):
        """Retrieves a user record by their unique username."""
=======
    @abstractmethod
    def get_user_by_username(self, username: str):
>>>>>>> origin/master
        pass

    @abstractmethod
    def create_user(self, username: str, hashed_pwd: str):
<<<<<<< HEAD
        """Persists a new user with a hashed password."""
        pass


class BaseZoneRepository(ABC):
    """Abstract base class defining the required contract for irrigation zone management."""

    @abstractmethod
    def get_all_zones(self) -> dict:
        """Retrieves all irrigation zones."""
        pass

    @abstractmethod
    def toggle_zone(self, zone_id: int, event_time: str) -> dict:
        """Toggles the status of a specific zone and records the event timestamp."""
        pass

    @abstractmethod
    def add_zone(self, name: str) -> dict:
        """Creates a new irrigation zone."""
        pass

    @abstractmethod
    def delete_zone(self, zone_id: int) -> bool:
        """Deletes an irrigation zone by its ID. Returns True if successful."""
        pass
=======
        pass
>>>>>>> origin/master
