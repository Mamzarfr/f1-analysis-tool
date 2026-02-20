import pytest
from fastapi.testclient import TestClient

from backend.app.database import session_maker
from backend.app.main import app


@pytest.fixture(scope="module")
def db():
    """Return db session"""
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client():
    """Return a TestClient to test the API endpoints"""
    return TestClient(app)
