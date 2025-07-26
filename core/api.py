import requests
import sqlite3
from core.db import store_prayer_times
API_URL = "https://api.aladhan.com/v1/timingsByCity"

def fetch_prayer_times_from_api(date, city, country=""):
    """Fetch prayer times from the API and store in DB."""
    params = {
        "city": city,
        "country": country,
        "method": 2,
        "date": date.strftime("%d-%m-%Y")
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()["data"]["timings"]
        print(f"API data extracted for {city}, {country} on {date}: {data}")  # Debug print
        times = {
            "Fajr": data["Fajr"],
            "Dhuhr": data["Dhuhr"],
            "Asr": data["Asr"],
            "Maghrib": data["Maghrib"],
            "Isha": data["Isha"]
        }
        store_prayer_times(date, city, times)
        return times
    except Exception as e:
        print(f"API error for {city}, {country} on {date}: {e}")  # Debug print
        raise Exception("Failed to fetch prayer times from API.")