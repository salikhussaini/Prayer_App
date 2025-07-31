import requests
from datetime import timedelta
from src.core.db import store_prayer_times,get_prayer_times_range_from_db
API_URL = "https://api.aladhan.com/v1/timingsByCity"
from datetime import datetime

def convert_to_24hr(time_str):
    """Convert 12-hour API time string like '4:51 AM' to 24-hour '04:51'."""
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return time_str  # fallback

def fetch_prayer_times_from_api(date, city, country=""):
    """Fetch prayer times from the API and store in DB in 24-hour format."""
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
            "Fajr": convert_to_24hr(data["Fajr"]),
            "Dhuhr": convert_to_24hr(data["Dhuhr"]),
            "Asr": convert_to_24hr(data["Asr"]),
            "Maghrib": convert_to_24hr(data["Maghrib"]),
            "Isha": convert_to_24hr(data["Isha"])
        }

        store_prayer_times(date, city, times)
        return times
    except Exception as e:
        print(f"API error for {city}, {country} on {date}: {e}")
        raise Exception("Failed to fetch prayer times from API.")
    
def ensure_future_data(city, country, days=7):
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    # Fetch from DB
    existing = get_prayer_times_range_from_db(today, end_date, city)

    # Determine which dates are missing
    missing_dates = []
    for i in range(days):
        date = today + timedelta(days=i)
        if date.strftime("%Y-%m-%d") not in existing:
            missing_dates.append(date)

    # If any are missing, fetch and store them
    for date in missing_dates:
        fetch_prayer_times_from_api(date, city, country)

    return True  # All data ensured
