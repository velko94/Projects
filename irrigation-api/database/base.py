"""
Abstract Repository Interfaces module.
Defines the base contracts (interfaces) for user and irrigation zone data operations,
ensuring strict decoupling and interchangeability between different database backends (PostgreSQL, DynamoDB).
"""

from abc import ABC, abstractmethod


class BaseUserRepository(ABC):
    """Abstract base class defining the required contract for user data operations."""

    @abstractmethod
    def get_user_by_username(self, username: str):
        """Retrieves a user record by their unique username."""
        pass

    @abstractmethod
    def create_user(self, username: str, hashed_pwd: str):
        """Persists a new user with a hashed password."""
        pass


class BaseZoneRepository(ABC):
    """Abstract base class defining the required contract for irrigation zone management."""

    @abstractmethod
    def get_zones_by_user(self, owner: str) -> dict:
        """Retrieves irrigation zones for a specific user."""
        pass

    @abstractmethod
    def get_all_zones(self) -> dict:
        """Retrieves all irrigation zones."""
        pass

    @abstractmethod
    def toggle_zone(self, zone_id: int, event_time: str, owner: str = None) -> dict: # type: ignore
        """Toggles the status of a specific zone."""
        pass

    @abstractmethod
    def add_zone(self, name: str, owner: str = "default_user") -> dict:
        """Creates a new irrigation zone."""
        pass

    @abstractmethod
    def delete_zone(self, zone_id: int, owner: str = None) -> bool: # type: ignore
        """Deletes an irrigation zone by its ID."""
        pass