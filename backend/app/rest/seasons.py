# Endpoints for seasons and events.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Driver, Event, Season
from backend.app.schemas import (
    DriverResponse,
    EventResponse,
    SeasonResponse,
)

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("", response_model=list[SeasonResponse])
def list_seasons(db: Session = Depends(get_db)):
    """Return all available seasons"""
    return db.query(Season).order_by(Season.year).all()


@router.get(
    "/{year}/events",
    response_model=list[EventResponse],
)
def list_events(year: int, db: Session = Depends(get_db)):
    """Return all events for a season year"""
    season = db.query(Season).filter(Season.year == year).first()
    if not season:
        raise HTTPException(
            status_code=404,
            detail=f"Season {year} not found",
        )
    return (
        db.query(Event)
        .filter(Event.season_year == year)
        .order_by(Event.round_number)
        .all()
    )


@router.get(
    "/{year}/drivers",
    response_model=list[DriverResponse],
)
def list_drivers(year: int, db: Session = Depends(get_db)):
    """Return all drivers for a given season"""
    season = db.query(Season).filter(Season.year == year).first()
    if not season:
        raise HTTPException(
            status_code=404,
            detail=f"Season {year} not found",
        )
    return db.query(Driver).filter(Driver.season_year == year).order_by(Driver.code).all()
