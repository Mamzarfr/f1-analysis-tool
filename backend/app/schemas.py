# Pydantic response schemas for the REST API.

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SeasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_year: int
    round_number: int
    name: str
    country: str
    circuit: str
    event_date: date


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    type: str
    date: datetime


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    team: str
    season_year: int


class LapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    driver_id: int
    lap_number: int
    lap_time: int | None
    sector1: int | None
    sector2: int | None
    sector3: int | None
    compound: str | None
    tire_life: int | None
    position: int | None
    top_speed: int | None
    full_throttle_pct: float | None
    brake_count: int | None


class LapDetailResponse(LapResponse):
    driver_code: str
