"""
Shared test fixtures and mock repositories for pytest.
"""

import pytest
from database.base import BaseUserRepository


class InMemoryUserRepository(BaseUserRepository):
    """Shared in-memory mock repository for isolated testing."""
    def __init__(self):
        self.storage = {}

    def get_user_by_username(self, username: str):
        if username in self.storage:
            return username, self.storage[username]
        return None

    def create_user(self, username: str, hashed_pwd: str):
        if username in self.storage:
            raise ValueError("User already exists")
        self.storage[username] = hashed_pwd
        return True


@pytest.fixture(autouse=True)
def override_repository(monkeypatch):
    """Globally injects the mock repository so tests never touch a real database."""
    mock_repo = InMemoryUserRepository()
    monkeypatch.setattr("database.factory.get_user_repository", lambda: mock_repo)
    return mock_repo