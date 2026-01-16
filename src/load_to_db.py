import json
import os
import sqlite3
from datetime import datetime, timezone

RAW_DIR = "data/raw"
DB_PATH = "data/weather.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_schema(conn):
    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def upsert_city(conn, city_name, lat, lon, country):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT city_id FROM dim_city
        WHERE city_name = ?
        """,
        (city_name,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO dim_city (city_name, latitude, longitude, country)
        VALUES (?, ?, ?, ?)
        """,
        (city_name, lat, lon, country)
    )
    return cursor.lastrowid


def upsert_weather_condition(conn, main, description):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT weather_condition_id
        FROM dim_weather_condition
        WHERE main = ? AND description = ?
        """,
        (main, description)
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO dim_weather_condition (main, description)
        VALUES (?, ?)
        """,
        (main, description)
    )
    return cursor.lastrowid


def upsert_fact_weather(conn, city_id, condition_id, data):
    cursor = conn.cursor()

    observation_timestamp = datetime.fromtimestamp(
        data["dt"], tz=timezone.utc
    ).isoformat()

    cursor.execute(
        """
        INSERT INTO fact_weather_hourly (
            city_id,
            weather_condition_id,
            observation_timestamp,
            temperature,
            feels_like,
            temp_min,
            temp_max,
            humidity,
            pressure,
            wind_speed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city_id, observation_timestamp)
        DO UPDATE SET
            weather_condition_id = excluded.weather_condition_id,
            temperature = excluded.temperature,
            feels_like = excluded.feels_like,
            temp_min = excluded.temp_min,
            temp_max = excluded.temp_max,
            humidity = excluded.humidity,
            pressure = excluded.pressure,
            wind_speed = excluded.wind_speed
        """,
        (
            city_id,
            condition_id,
            observation_timestamp,
            data["main"]["temp"],
            data["main"]["feels_like"],
            data["main"]["temp_min"],
            data["main"]["temp_max"],
            data["main"]["humidity"],
            data["main"]["pressure"],
            data["wind"]["speed"],
        )
    )


def main():
    print("🗄️  Inizio caricamento dati nel database...")

    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    load_schema(conn)

    for file in os.listdir(RAW_DIR):
        if not file.endswith(".json"):
            continue

        with open(os.path.join(RAW_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        city_name = data["name"].lower()
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]
        country = data["sys"].get("country")

        city_id = upsert_city(conn, city_name, lat, lon, country)

        weather = data["weather"][0]
        condition_id = upsert_weather_condition(
            conn,
            weather["main"],
            weather["description"]
        )

        upsert_fact_weather(conn, city_id, condition_id, data)

    conn.commit()
    conn.close()

    print("✅ Caricamento completato con successo")


if __name__ == "__main__":
    main()
