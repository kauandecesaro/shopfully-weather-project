import sqlite3
import pandas as pd

DB_PATH = "data/weather.db"


def load_denormalized_df(db_path: str) -> pd.DataFrame:
    """
    Carrega um dataframe denormalizzato (fact + dimension) dal database SQLite.
    """
    query = """
    SELECT
        c.city_name,
        wc.main AS weather_condition,
        wc.description AS weather_description,
        f.observation_timestamp,
        f.temperature,
        f.feels_like,
        f.temp_min,
        f.temp_max,
        f.humidity,
        f.pressure,
        f.wind_speed
    FROM fact_weather_hourly f
    JOIN dim_city c
        ON f.city_id = c.city_id
    JOIN dim_weather_condition wc
        ON f.weather_condition_id = wc.weather_condition_id
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Parse timestamp
    df["observation_timestamp"] = pd.to_datetime(df["observation_timestamp"], utc=True)
    df["date"] = df["observation_timestamp"].dt.date

    return df


def main():
    print("📊 Avvio analisi con pandas (dataframe denormalizzato)...\n")

    df = load_denormalized_df(DB_PATH)

    if df.empty:
        print("⚠️ Nessun dato trovato nel database. Esegui prima fetch_weather.py e load_to_db.py.")
        return

    # Se vuoi filtrare un periodo, puoi usare queste due righe:
    # start_date = pd.Timestamp("2026-01-01", tz="UTC")
    # end_date = pd.Timestamp("2026-12-31", tz="UTC")
    # df = df[(df["observation_timestamp"] >= start_date) & (df["observation_timestamp"] <= end_date)]

    # 1) Numero di condizioni meteo distinte nel periodo (basato su 'main')
    distinct_conditions = df["weather_condition"].nunique()

    # 2) Ranking condizioni più comuni per città
    ranking = (
        df.groupby(["city_name", "weather_condition"])
        .size()
        .reset_index(name="occurrences")
        .sort_values(["city_name", "occurrences"], ascending=[True, False])
    )

    # 3) Temperatura media per città
    avg_temp = (
        df.groupby("city_name")["temperature"]
        .mean()
        .reset_index(name="avg_temperature")
        .sort_values("avg_temperature", ascending=False)
    )

    # 4) Città con temperatura massima assoluta nel periodo (temp_max)
    max_abs = (
        df.groupby("city_name")["temp_max"]
        .max()
        .reset_index(name="max_temperature")
        .sort_values("max_temperature", ascending=False)
        .head(1)
    )

    # 5) Città con maggiore variazione giornaliera (max(temp_max) - min(temp_min) per giorno)
    daily_variation = (
        df.groupby(["city_name", "date"])
        .agg(daily_max=("temp_max", "max"), daily_min=("temp_min", "min"))
        .assign(daily_variation=lambda x: x["daily_max"] - x["daily_min"])
        .reset_index()
        .sort_values("daily_variation", ascending=False)
        .head(1)
    )

    # 6) Città con vento massimo
    max_wind = (
        df.groupby("city_name")["wind_speed"]
        .max()
        .reset_index(name="max_wind_speed")
        .sort_values("max_wind_speed", ascending=False)
        .head(1)
    )

    # Output
    print(f"1) Condizioni meteo distinte nel periodo: {distinct_conditions}\n")

    print("2) Ranking condizioni meteo per città:")
    print(ranking.to_string(index=False))
    print()

    print("3) Temperatura media per città:")
    print(avg_temp.to_string(index=False))
    print()

    print("4) Città con temperatura massima assoluta:")
    print(max_abs.to_string(index=False))
    print()

    print("5) Città con maggiore variazione giornaliera:")
    print(daily_variation.to_string(index=False))
    print()

    print("6) Città con vento massimo:")
    print(max_wind.to_string(index=False))
    print()

    print("✅ Analisi completata")


if __name__ == "__main__":
    main()
