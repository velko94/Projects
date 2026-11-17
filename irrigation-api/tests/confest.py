"""
Shared test fixtures and database initialization for pytest.
"""

import pytest
from database.connection import Base, engine
from database.postgres_repo import init_db

# start the tables in the db uppon running the confest
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensures database tables exist before running test suite."""
    init_db()