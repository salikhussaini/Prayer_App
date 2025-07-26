from src.core.db import get_prayer_times_from_db, store_prayer_times
from src.core.api import fetch_prayer_times_from_api

def calculate_prayer_times(date, location):
    city = location.get("city", "")
    country = location.get("country", "")
    times = get_prayer_times_from_db(date, city)
    if times:
        print(f"Data found for {city}, {country} on {date}: {times}")
        return times
    print(f"No data found for {city}, {country} on {date}.")
    try:
        times = fetch_prayer_times_from_api(date, city, country)
        return times
    except Exception as e:
        print(f"API fetch failed for {city}, {country} on {date}: {e}")
        raise Exception("Failed to calculate prayer times.")