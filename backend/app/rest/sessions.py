# Endpoints for sessions, laps and drivers per session.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Driver, Lap
from backend.app.models import Session as SessionModel
from backend.app.schemas import DriverResponse, LapDetailResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get(
    "/{session_id}/drivers",
    response_model=list[DriverResponse],
)
def list_session_drivers(session_id: int, db: Session = Depends(get_db)):
    """Return all drivers who drove in a session"""
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )

    driver_ids = (
        db.query(Lap.driver_id)
        .filter(Lap.session_id == session_id)
        .distinct()
    )
    return (
        db.query(Driver)
        .filter(Driver.id.in_(driver_ids))
        .order_by(Driver.code)
        .all()
    )


@router.get(
    "/{session_id}/laps",
    response_model=list[LapDetailResponse],
)
def list_session_laps(session_id: int,
                      driver: str | None = Query(
                          None, description="Filter by driver code"
                      ),
                      compound: str | None = Query(
                          None, description="Filter by compound"
                      ),
                      lap_min: int | None = Query(
                          None, description="Minimum lap number"
                      ),
                      lap_max: int | None = Query(
                          None, description="Maximum lap number"
                      ),
                      db: Session = Depends(get_db)):
    """Return laps for a session with filters"""
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )

    query = (
        db.query(Lap, Driver.code)
        .join(Driver, Lap.driver_id == Driver.id)
        .filter(Lap.session_id == session_id)
    )
    query = aux_apply_filters(
        query, driver, compound, lap_min, lap_max
    )
    query = query.order_by(Lap.lap_number, Driver.code)
    return aux_build_resp(query.all())


def aux_apply_filters(
        query, driver, compound, lap_min, lap_max
):
    """Apply optional query parameter filters"""
    if driver:
        query = query.filter(
            Driver.code == driver.upper()
        )
    if compound:
        query = query.filter(
            Lap.compound == compound.upper()
        )
    if lap_min is not None:
        query = query.filter(Lap.lap_number >= lap_min)
    if lap_max is not None:
        query = query.filter(Lap.lap_number <= lap_max)
    return query


def aux_build_resp(rows) -> list[dict]:
    """Convert (Lap, driver_code) to responses."""
    res = []
    for lap, driver_code in rows:
        lap.driver_code = driver_code
        data = LapDetailResponse.model_validate(lap)
        res.append(data)
    return res
