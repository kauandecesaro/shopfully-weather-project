-- =========================
-- DIMENSION: CITY
-- =========================
CREATE TABLE IF NOT EXISTS dim_city (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    country TEXT
);

-- =========================
-- DIMENSION: WEATHER CONDITION
-- =========================
CREATE TABLE IF NOT EXISTS dim_weather_condition (
    weather_condition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    main TEXT NOT NULL,
    description TEXT NOT NULL
);

-- =========================
-- FACT: HOURLY WEATHER
-- =========================
CREATE TABLE IF NOT EXISTS fact_weather_hourly (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    weather_condition_id INTEGER NOT NULL,
    observation_timestamp TEXT NOT NULL, -- ISO-8601 UTC (es. 2026-01-16T12:00:00+00:00)

    temperature REAL,
    feels_like REAL,
    temp_min REAL,
    temp_max REAL,
    humidity INTEGER,
    pressure INTEGER,
    wind_speed REAL,

    FOREIGN KEY (city_id) REFERENCES dim_city(city_id),
    FOREIGN KEY (weather_condition_id) REFERENCES dim_weather_condition(weather_condition_id),

    -- Chiave naturale per granularità oraria + supporto UPSERT
    UNIQUE (city_id, observation_timestamp)
);

-- =========================
-- INDEXES FOR ANALYTICS
-- =========================
CREATE INDEX IF NOT EXISTS idx_weather_timestamp
    ON fact_weather_hourly (observation_timestamp);

CREATE INDEX IF NOT EXISTS idx_weather_city
    ON fact_weather_hourly (city_id);

CREATE INDEX IF NOT EXISTS idx_weather_condition
    ON fact_weather_hourly (weather_condition_id);
