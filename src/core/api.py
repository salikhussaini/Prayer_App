import requests
from datetime import timedelta, datetime
from src.core.db import store_prayer_times, get_prayer_times_range_from_db
import re
API_URL_SINGLE = "https://api.aladhan.com/v1/timingsByCity"

def convert_to_24hr(time_str):
    """Convert 12-hour API time string like '4:51 AM' to 24-hour '04:51'."""
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return time_str  # fallback
def clean_timezone_suffix(s):
    """Remove timezone suffix like '(CST)' from time strings."""
    return re.sub(r"\s*\(?[A-Z]{2,4}\)?\s*$", "", s).strip()

def fetch_prayer_times_from_api(date, city, country=""):
    """Fetch prayer times from the single-date API and store in DB in 24-hour format."""
    params = {
        "city": city,
        "country": country,
        "method": 2,   # Islamic Society of North America
        "date": date.strftime("%d-%m-%Y"),
        "school": 1    # Hanafi
    }
    try:
        response = requests.get(API_URL_SINGLE, params=params)
        response.raise_for_status()
        data = response.json()["data"]["timings"]
        print(f"API data extracted for {city}, {country} on {date}: {data}")

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
    
def fetch_prayer_times_range(start_date, end_date, city, country=""):
    """Fetch prayer times for a date range from the new API and store each day in DB."""
    url = f"https://api.aladhan.com/v1/calendarByCity/from/{start_date.strftime('%d-%m-%Y')}/to/{end_date.strftime('%d-%m-%Y')}"
    
    params = {
        "city": city,
        "country": country,
        "method": 2,    # Same method as single-day
        "school": 1,
        "calendarMethod": "HJCoSA",
        "iso8601": "false",
        # add more params if needed
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # The API returns data in data.data array for each day
        for day_data in data.get("data", []):
            greg_date_str = day_data["date"]["gregorian"]["date"]  # e.g. "01-02-2025"
            date = datetime.strptime(greg_date_str, "%d-%m-%Y").date()
            timings = day_data["timings"]
            
            times = {
                "Fajr": convert_to_24hr(clean_timezone_suffix(timings["Fajr"])),
                "Dhuhr": convert_to_24hr(clean_timezone_suffix(timings["Dhuhr"])),
                "Asr": convert_to_24hr(clean_timezone_suffix(timings["Asr"])),
                "Maghrib": convert_to_24hr(clean_timezone_suffix(timings["Maghrib"])),
                "Isha": convert_to_24hr(clean_timezone_suffix(timings["Isha"]))
            }

            store_prayer_times(date, city, times)
        print(f"Stored prayer times for {city} on between {start_date} and {end_date} successfully.")

        return True
    except Exception as e:
        print(f"Error fetching date range prayer times: {e}")
        return False

def ensure_future_data(city, country="", days=7):
    """Ensure prayer times for the next 'days' days are available in DB."""
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    # Fetch existing data from DB
    existing = get_prayer_times_range_from_db(today, end_date, city)

    # Check which dates are missing
    missing_dates = []
    for i in range(days):
        date = today + timedelta(days=i)
        if date.strftime("%Y-%m-%d") not in existing:
            missing_dates.append(date)

    if not missing_dates:
        print(f"All data present for {city} between {today} and {end_date}")
        return True

    # Instead of fetching day-by-day, fetch all missing dates in one range if possible
    range_start = min(missing_dates)
    range_end = max(missing_dates)
    success = fetch_prayer_times_range(range_start, range_end, city, country)

    if not success:
        # Fallback: fetch missing dates individually
        for date in missing_dates:
            try:
                fetch_prayer_times_from_api(date, city, country)
            except Exception:
                print(f"Failed to fetch prayer times for {date}, {city}")

    return True
