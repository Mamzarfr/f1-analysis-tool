# SQLAlchemy ORM models (same as schema.sql).

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Season(Base):
    """Seasons table from the database schema."""
    __tablename__ = "seasons"

    year: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="season",
        order_by="Event.round_number",
    )


class Event(Base):
    """Events table from the database schema."""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_year: Mapped[int] = mapped_column(
        ForeignKey("seasons.year")
    )

    round_number: Mapped[int]
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    circuit: Mapped[str] = mapped_column(String(100))
    event_date: Mapped[date] = mapped_column(Date)

    season: Mapped["Season"] = relationship(
        back_populates="events"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="event"
    )


class Session(Base):
    """Sessions table from the database schema."""
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    type: Mapped[str] = mapped_column(
        Enum(
            "FP1", "FP2", "FP3", "Q", "SQ", "S", "R",
            name="session_type",
            create_type=False,
        )
    )

    date: Mapped[datetime] = mapped_column(DateTime)

    event: Mapped["Event"] = relationship(
        back_populates="sessions"
    )
    laps: Mapped[list["Lap"]] = relationship(
        back_populates="session"
    )
    pit_stops: Mapped[list["PitStop"]] = relationship(
        back_populates="session"
    )


class Driver(Base):
    """Drivers table from the database schema."""
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3))
    name: Mapped[str] = mapped_column(String(100))
    team: Mapped[str] = mapped_column(String(100))
    season_year: Mapped[int] = mapped_column(
        ForeignKey("seasons.year")
    )


class Lap(Base):
    """Laps table from the database schema."""
    __tablename__ = "laps"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id")
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id")
    )

    lap_number: Mapped[int]
    lap_time: Mapped[int | None]
    sector1: Mapped[int | None]
    sector2: Mapped[int | None]
    sector3: Mapped[int | None]
    compound: Mapped[str | None] = mapped_column(
        String(20)
    )
    tire_life: Mapped[int | None]
    position: Mapped[int | None]
    top_speed: Mapped[int | None]
    full_throttle_pct: Mapped[float | None] = (
        mapped_column(Float)
    )
    brake_count: Mapped[int | None]

    session: Mapped["Session"] = relationship(
        back_populates="laps"
    )
    driver: Mapped["Driver"] = relationship()


class PitStop(Base):
    """Pit_stops table from the database schema."""
    __tablename__ = "pit_stops"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id")
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id")
    )
    lap_number: Mapped[int]
    duration: Mapped[int | None]

    session: Mapped["Session"] = relationship(
        back_populates="pit_stops"
    )
    driver: Mapped["Driver"] = relationship()
