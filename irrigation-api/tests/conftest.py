"""
Shared test fixtures and database initialization for pytest.
"""

import pytest
from database.connection import Base, engine ,User
from database.postgres_repo import ZoneModel , init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
   """Automatically creates all database tables (users, zones) in PostgreSQL before running tests."""
   Base.metadata.create_all(bind=engine)
   init_db()