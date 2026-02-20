import pytest
from fastapi.testclient import TestClient

from backend.app.database import session_maker
from backend.app.main import app
from backend.app.models import Driver, Event, Lap, Season, Session

TEST_YEAR = 6767


def _test_data(db):
    """Insert test data"""
    season = Season(year=TEST_YEAR)
    db.add(season)
    db.flush()

    event = Event(
        season_year=TEST_YEAR,
        round_number=1,
        name="Test Grand Prix",
        country="Testland",
        circuit="Test Circuit",
        event_date="2025-03-15",
    )
    db.add(event)
    db.flush()

    session = Session(event_id=event.id, type="R", date="2025-03-15 14:00:00")
    db.add(session)
    db.flush()

    driver = Driver(
        code="TST",
        name="Test Driver",
        team="Test Team",
        season_year=TEST_YEAR,
    )
    db.add(driver)
    db.flush()

    for i in range(1, 4):
        db.add(
            Lap(
                session_id=session.id,
                driver_id=driver.id,
                lap_number=i,
                lap_time=90000 + i * 100,
                sector1=30000,
                sector2=30000,
                sector3=30000,
                compound="SOFT",
                tire_life=i,
                position=1,
                top_speed=310,
                full_throttle_pct=25.0,
                brake_count=10,
            )
        )

    db.commit()


@pytest.fixture(scope="session", autouse=True)
def fill_test_db():
    """Fill the test database with initial data once"""
    db = session_maker()
    try:
        _test_data(db)
        yield
    finally:
        db.rollback()
        db.close()


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
