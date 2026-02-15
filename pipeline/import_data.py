# F1 Data Import Pipeline to feed database with session data from FastF1.

from logging import basicConfig, getLogger, INFO

import numpy as np
import pandas as pd
import psycopg2.extensions
from fastf1 import Cache, get_session, get_event_schedule

psycopg2.extensions.register_adapter(np.int64, lambda val: psycopg2.extensions.AsIs(int(val)))
psycopg2.extensions.register_adapter(np.float64, lambda val: psycopg2.extensions.AsIs(float(val)))

from backend.app.database import get_connection

basicConfig(level=INFO)
logger = getLogger(__name__)

Cache.enable_cache("./ff1_cache")

# Mapping of FastF1 session names to database names
TYPE_TABLE = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Qualifying": "Q",
    "Sprint Qualifying": "SQ",
    "Sprint": "S",
    "Race": "R",
}


def import_session(year: int, event_name: str, session_type: str):
    """
    Import a complete session into the database.

    :param year: The season year
    :param event_name: The name of the event ("Silverstone", "Monza", etc)
    :param session_type: The type of session, one of TYPE_TABLE values
    :raises Exception: If any database operation fails, rolls back and raises
    """
    session = get_session(year, event_name, session_type)
    session.load()

    con = get_connection()
    cur = con.cursor()

    try:
        _insert_season(cur, year)
        event_id = _insert_event(cur, session, year)
        session_id = _insert_session(cur, session, event_id)
        driver_ids = _insert_drivers(cur, session, year)
        _insert_laps(cur, session, session_id, driver_ids)
        _insert_pits(cur, session, session_id, driver_ids)

        con.commit()
        logger.info(f"Imported: {year} {event_name} {session_type}")
    except Exception as e:
        con.rollback()
        raise e
    finally:
        cur.close()
        con.close()


def _insert_season(cur, year: int):
    """
    Insert a season into the database if missing.

    :param cur: Database cursor
    :param year: The season year
    """
    cur.execute(
        "INSERT INTO seasons (year) VALUES (%s) ON CONFLICT DO NOTHING",
        (year,)
    )


def _insert_event(cur, session, year: int) -> int:
    """
    Insert an event into the database and return its ID.

    :param cur: Database cursor
    :param session: FastF1 session object
    :param year: The season year
    :return: The database ID of the inserted/existing event
    """
    event = session.event
    cur.execute(
        """
        INSERT INTO events (season_year, round_number, name, country, circuit, event_date)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        RETURNING id
        """,
        (
            year,
            event["RoundNumber"],
            event["EventName"],
            event["Country"],
            event["Location"],
            event["EventDate"],
        )
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "SELECT id FROM events WHERE season_year = %s AND round_number = %s",
        (year, event["RoundNumber"])
    )
    return cur.fetchone()[0]


def _insert_session(cur, session, event_id: int) -> int:
    """
    Insert a session into the database and return its ID.

    :param cur: Database cursor
    :param session: FastF1 session object
    :param event_id: The database ID of the parent event
    :return: The ID of the new session
    """
    session_type = TYPE_TABLE.get(session.name, session.name)
    cur.execute(
        """
        INSERT INTO sessions (event_id, type, date)
        VALUES (%s, %s, %s) ON CONFLICT (event_id, type) DO NOTHING
        RETURNING id
        """,
        (event_id, session_type, session.date)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "SELECT id FROM sessions WHERE event_id = %s AND type = %s",
        (event_id, session_type)
    )
    return cur.fetchone()[0]


def _insert_drivers(cur, session, year: int) -> dict[str, int]:
    """
    Insert drivers from a session into the database

    :param cur: Database cursor
    :param session: FastF1 session object
    :param year: The season year
    :return: A dictionary mapping driver codes to their db ID.
    """
    driver_ids = {}
    for _, driver in session.results.iterrows():
        code = driver["Abbreviation"]
        cur.execute(
            """
            INSERT INTO drivers (code, name, team, season_year)
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
            RETURNING id
            """,
            (code, driver["FullName"], driver["TeamName"], year)
        )
        row = cur.fetchone()
        if row:
            driver_ids[code] = row[0]
        else:
            cur.execute(
                "SELECT id FROM drivers WHERE code = %s AND season_year = %s",
                (code, year)
            )
            driver_ids[code] = cur.fetchone()[0]
    return driver_ids


def _insert_laps(cur, session, session_id: int, driver_ids: dict[str, int]):
    """
    Insert lap data from a session into the database.

    :param cur: Database cursor
    :param session: FastF1 session object
    :param session_id: The session ID in the database
    :param driver_ids: Dictionary mapping driver codes to their db ID.
    """
    laps = session.laps
    for _, lap in laps.iterlaps():
        driver = lap["Driver"]
        if driver not in driver_ids:
            continue
        top_speed, throttle_pct, brakes = _get_telemetry(lap)
        cur.execute(
            """
            INSERT INTO laps (session_id, driver_id, lap_number, lap_time,
                              sector1, sector2, sector3, compound, tire_life,
                              position, top_speed, full_throttle_pct, brake_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session_id,
                driver_ids[driver],
                lap["LapNumber"],
                _to_ms(lap["LapTime"]),
                _to_ms(lap["Sector1Time"]),
                _to_ms(lap["Sector2Time"]),
                _to_ms(lap["Sector3Time"]),
                lap.get("Compound"),
                _safe_int(lap.get("TyreLife")),
                _safe_int(lap.get("Position")),
                top_speed,
                throttle_pct,
                brakes,
            )
        )


def _insert_pits(cur, session, session_id: int, driver_ids: dict[str, int]):
    """
    Insert all pit stops from a session into the database.

    :param cur: Database cursor
    :param session: FastF1 session object
    :param session_id: The db ID of the session
    :param driver_ids: Dictionary mapping driver codes to their db ID.
    """
    laps = session.laps
    pit_laps = laps[laps["PitInTime"].notna()]
    for _, lap in pit_laps.iterrows():
        driver = lap["Driver"]
        if driver not in driver_ids:
            continue
        pit_time = lap.get("PitOutTime") - lap.get("PitInTime")
        cur.execute(
            """
            INSERT INTO pit_stops (session_id, driver_id, lap_number, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (
                session_id,
                driver_ids[driver],
                lap["LapNumber"],
                _to_ms(pit_time),
            )
        )


def _get_telemetry(lap) -> tuple:
    try:
        car = lap.get_car_data()
        if car is None or car.empty:
            return None, None, None
        top_speed = int(car['Speed'].max())
        full_throttle_pct = round(
            (car['Throttle'] >= 99).mean() * 100, 1
        )
        brake_count = int(
            (car['Brake'].astype(int).diff() > 0).sum()
        )
        return top_speed, full_throttle_pct, brake_count
    except Exception:
        return None, None, None


def _safe_int(val) -> int | None:
    """
    Handle NaN and infinite values before giving them to the db.

    :param val: A numeric value or NaN/inf
    :return: The value as an integer, or None if the value is NaN, -inf or inf
    """
    if pd.isna(val) or not np.isfinite(val):
        return None
    return int(val)


def _to_ms(td) -> int | None:
    """
    Convert pandas timedeltas to milliseconds.

    :param td: Timedelta or NaT
    :return: The time in milliseconds as an int, None if td is NaT/NaN
    """
    if pd.isna(td):
        return None
    return int(td.total_seconds() * 1000)


def import_season(year: int):
    """
    Import all sessions from a season into the database.

    :param year: The season year to import
    """
    sch = get_event_schedule(year, include_testing=False)
    types = ["S", "FP1", "FP2", "FP3", "Q", "SQ", "R"]

    for _, event in sch.iterrows():
        event_name = event["EventName"]
        for st in types:
            try:
                import_session(year, event_name, st)
            except Exception as e:
                logger.warning(f"Skipped {event_name} {st}: {e}")


if __name__ == "__main__":
    import_season(2024)
