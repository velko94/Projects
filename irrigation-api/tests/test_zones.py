"""
Unit tests for irrigation zone management logic:
1. Retrieving all available irrigation zones.
2. Toggling zone operational state ('on'/'off') and updating timestamps.
3. Adding new irrigation zones and preventing duplicate names.
4. Deleting irrigation zones by ID.
"""

import pytest
from fastapi import HTTPException
from database.base import BaseZoneRepository


class InMemoryZoneRepository(BaseZoneRepository): # type: ignore
    """In-memory mock repository for testing zone operations without a real database."""

    def __init__(self):
        # Pre-populate with a couple of mock zones for testing
        self.storage = {
            1: {"name": "Greenhouse Zone", "status": "off", "last_watered": "Never"},
            2: {"name": "Lawn Sprinklers", "status": "on", "last_watered": "2026-06-01 10:00:00"}
        }
        self.next_id = 3

    def get_all_zones(self) -> dict: # type: ignore
        """Retrieves all zones from in-memory storage."""
        return self.storage

    def toggle_zone(self, zone_id: int, event_time: str) -> dict: # type: ignore
        """Toggles zone status and updates last watered time if turned 'on'."""
        if zone_id not in self.storage:
            return None # type: ignore

        zone = self.storage[zone_id]
        if zone["status"] == "off":
            zone["status"] = "on"
            zone["last_watered"] = event_time
        else:
            zone["status"] = "off"

        return zone

    def add_zone(self, name: str) -> dict: # type: ignore
        """Adds a new zone if the name is unique."""
        for z in self.storage.values():
            if z["name"] == name:
                raise HTTPException(status_code=400, detail="A zone with this name already exists!")

        new_id = self.next_id
        self.next_id += 1

        new_zone = {
            "id": new_id,
            "name": name,
            "status": "off",
            "last_watered": "Never"
        }
        self.storage[new_id] = new_zone # type: ignore
        return new_zone

    def delete_zone(self, zone_id: int) -> bool: # type: ignore
        """Deletes a zone by ID if it exists."""
        if zone_id in self.storage:
            del self.storage[zone_id]
            return True
        return False


@pytest.fixture(autouse=True)
def override_zone_repository(monkeypatch):
    """Fixture to inject the in-memory zone mock repository."""
    mock_zone_repo = InMemoryZoneRepository() # type: ignore
    monkeypatch.setattr("database.factory.get_zone_repository", lambda: mock_zone_repo)
    return mock_zone_repo


def test_get_all_zones():
    """Test 1: Successfully retrieves all pre-configured zones."""
    repo = InMemoryZoneRepository() # type: ignore
    zones = repo.get_all_zones()

    assert len(zones) == 2
    assert zones[1]["name"] == "Greenhouse Zone"
    assert zones[2]["status"] == "on"


def test_toggle_zone_state():
    """Test 2: Toggling a zone flips its status and updates the timestamp when activated."""
    repo = InMemoryZoneRepository() # type: ignore
    timestamp = "2026-06-06 12:00:00"

    # Toggle Zone 1 from 'off' to 'on'
    updated = repo.toggle_zone(1, timestamp)
    assert updated["status"] == "on"
    assert updated["last_watered"] == timestamp

    # Toggle Zone 1 again from 'on' back to 'off'
    updated_again = repo.toggle_zone(1, timestamp)
    assert updated_again["status"] == "off"


def test_add_zone_success_and_duplicate():
    """Test 3: Adding a new zone succeeds, while adding a duplicate name raises HTTP 400."""
    repo = InMemoryZoneRepository() # type: ignore

    # Add a unique new zone
    new_zone = repo.add_zone("Orchard Section")
    assert new_zone["name"] == "Orchard Section"
    assert new_zone["status"] == "off"

    # Attempting to add a zone with an existing name should raise HTTP 400
    with pytest.raises(HTTPException) as exc_info:
        repo.add_zone("Greenhouse Zone")

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail # type: ignore


def test_delete_zone():
    """Test 4: Deleting a zone removes it from storage successfully."""
    repo = InMemoryZoneRepository() # type: ignore

    # Delete existing zone 2
    success = repo.delete_zone(2)
    assert success is True

    zones = repo.get_all_zones()
    assert 2 not in zones

    # Deleting non-existent zone should return False
    assert repo.delete_zone(999) is False