import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# =====================
# ENV
# =====================
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise ValueError("API key non trovata. Verifica il file .env")

# =====================
# CONFIG
# =====================
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CITIES = {
    "milano": {"lat": 45.4642, "lon": 9.1900},
    "bologna": {"lat": 44.4949, "lon": 11.3426},
    "cagliari": {"lat": 39.2238, "lon": 9.1217},
}

RAW_DIR = "data/raw"

# =====================
# FUNCTIONS
# =====================
def fetch_weather(city, lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "appid": API_KEY,
        "lang": "it"
    }

    headers = {
        "User-Agent": "shopfully-weather-pipeline/1.0"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def save_raw(data, city):
    os.makedirs(RAW_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{RAW_DIR}/{city}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================
# MAIN
# =====================
def main():
    print("🌤️  Avvio della raccolta dei dati meteorologici...\n")

    for city, coords in CITIES.items():
        try:
            data = fetch_weather(city, coords["lat"], coords["lon"])
            save_raw(data, city)
            print(f"✅ Dati salvati per {city}")
        except Exception as e:
            print(f"❌ Errore durante l'elaborazione di {city}: {e}")

    print("\n🚀 Raccolta completata con successo")


if __name__ == "__main__":
    main()
