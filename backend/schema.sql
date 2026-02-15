CREATE TYPE session_type AS ENUM ( 'FP1', 'FP2', 'FP3', 'Q', 'SQ', 'S', 'R' );

CREATE TABLE seasons (
    year INTEGER PRIMARY KEY
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    season_year INTEGER NOT NULL REFERENCES seasons(year),
    round_number INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    circuit VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id),
    type session_type NOT NULL,
    date TIMESTAMP NOT NULL
);

CREATE TABLE drivers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL,
    name VARCHAR(100) NOT NULL,
    team VARCHAR(100) NOT NULL,
    season_year INTEGER NOT NULL REFERENCES seasons(year)
);

CREATE TABLE laps (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    driver_id INTEGER NOT NULL REFERENCES drivers(id),
    lap_number INTEGER NOT NULL,
    lap_time INTEGER,
    sector1 INTEGER,
    sector2 INTEGER,
    sector3 INTEGER,
    compound VARCHAR(20),
    tire_life INTEGER,
    position INTEGER,
    top_speed INTEGER,
    full_throttle_pct REAL,
    brake_count INTEGER
);

CREATE TABLE pit_stops (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    driver_id INTEGER NOT NULL REFERENCES drivers(id),
    lap_number INTEGER NOT NULL,
    duration INTEGER
);
