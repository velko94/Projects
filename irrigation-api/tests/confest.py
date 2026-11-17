"""
Shared test fixtures and database initialization for pytest.
"""

import pytest
from database.postgres_repo import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Automatically creates all database tables in PostgreSQL before running tests."""
    init_db()