"""
API integration, location utilities, and update checking for Prayer App.
Combines prayer time fetching, geolocation, and system update functionality.
"""

import requests
import time
import logging
import os
import subprocess
import platform
from datetime import timedelta, datetime
from pathlib import Path
import re

from src.core.db import store_prayer_times, get_prayer_times_range_from_db
import src.core.config as config


# Setup logging
logger = logging.getLogger(__name__)

# Custom Exceptions
class PrayerAPIException(Exception):
    """Base exception for prayer API errors."""
    pass


class PrayerAPIConnectionError(PrayerAPIException):
    """Raised when connection to API fails."""
    pass


class PrayerAPIResponseError(PrayerAPIException):
    """Raised when API response is invalid or malformed."""
    pass


class PrayerAPIRateLimit(PrayerAPIException):
    """Raised when API rate limit is exceeded."""
    pass


def convert_to_24hr(time_str):
    """Convert prayer time to 24-hour format.
    
    Handles both:
    - 12-hour format with AM/PM (e.g., '4:51 AM')
    - 24-hour format (e.g., '03:33')
    
    Args:
        time_str (str): Time string in either format
        
    Returns:
        str: Time in 24-hour HH:MM format
    """
    if not time_str or not isinstance(time_str, str):
        logger.warning(f"Invalid time string: {time_str}")
        return time_str
    
    time_str = time_str.strip()
    
    # Check if it's already in 24-hour format (contains only digits and colon)
    # e.g., "03:33" or "12:50" (no AM/PM)
    if ':' in time_str and not any(c.isalpha() for c in time_str):
        # Already in 24-hour format
        return time_str
    
    # Try parsing as 12-hour format with AM/PM
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        logger.warning(f"Could not parse time string in standard formats: {time_str}")
        return time_str  # Fallback to original


def clean_timezone_suffix(s):
    """Remove timezone suffix like '(CST)' from time strings."""
    return re.sub(r"\s*\(?[A-Z]{2,4}\)?\s*$", "", s).strip()


def fetch_prayer_times_from_api(date, city, country="", max_retries=None):
    """Fetch prayer times from single-date API and store in DB in 24-hour format.
    
    Args:
        date: datetime.date object
        city: City name
        country: Country name
        max_retries: Maximum retry attempts on failure (uses API_MAX_RETRIES if None)
        
    Returns:
        dict: Prayer times in {'Prayer': 'HH:MM'} format
        
    Raises:
        PrayerAPIConnectionError: Network/connection issues
        PrayerAPIResponseError: Invalid API response
        PrayerAPIRateLimit: API rate limit exceeded
    """
    if max_retries is None:
        max_retries = config.API_MAX_RETRIES
    
    params = {
        "city": city,
        "country": country,
        "method": config.API_METHOD,
        "date": date.strftime("%d-%m-%Y"),
        "school": config.API_SCHOOL
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(config.API_URL_SINGLE, params=params, timeout=config.API_TIMEOUT)
            
            # Handle rate limiting
            if response.status_code == 429:
                raise PrayerAPIRateLimit("API rate limit exceeded")
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            response_json = response.json()["data"]
            data = response_json["timings"]
            greg_date_str = response_json["date"]["gregorian"]["date"]
            hijri_date_str = response_json["date"]["hijri"]["date"]
            
            # Convert to datetime object
            date_obj = datetime.strptime(greg_date_str, "%d-%m-%Y").date()

            times = {
                "Fajr": convert_to_24hr(data["Fajr"]),
                "Dhuhr": convert_to_24hr(data["Dhuhr"]),
                "Asr": convert_to_24hr(data["Asr"]),
                "Maghrib": convert_to_24hr(data["Maghrib"]),
                "Isha": convert_to_24hr(data["Isha"])
            }

            store_prayer_times(date_obj, hijri_date_str, city, times)
            logger.info(f"Successfully fetched prayer times for {city}, {country} on {date}")
            return times
            
        except requests.ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = config.API_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
            else:
                raise PrayerAPIConnectionError(f"Failed to connect after {max_retries} attempts: {e}")
                
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise PrayerAPIRateLimit(f"API rate limit exceeded: {e}")
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise PrayerAPIResponseError(f"API HTTP error: {e}")
            
        except requests.Timeout as e:
            logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                continue
            else:
                raise PrayerAPIConnectionError(f"Request timeout after {max_retries} attempts: {e}")
                
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid API response format: {e}")
            raise PrayerAPIResponseError(f"Failed to parse API response: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error fetching prayer times: {e}", exc_info=True)
            raise PrayerAPIException(f"Unexpected error: {e}")


    
def fetch_prayer_times_range(start_date, end_date, city, country="", max_retries=None):
    """Fetch prayer times for a date range from API and store each day in DB.
    
    Args:
        start_date: datetime.date start of range
        end_date: datetime.date end of range
        city: City name
        country: Country name
        max_retries: Maximum retry attempts on failure (uses API_MAX_RETRIES if None)
        
    Returns:
        bool: True on success, False otherwise
        
    Raises:
        PrayerAPIConnectionError: Network/connection issues
        PrayerAPIResponseError: Invalid API response
        PrayerAPIRateLimit: API rate limit exceeded
    """
    if max_retries is None:
        max_retries = config.API_MAX_RETRIES
    
    url = f"{config.API_URL_CALENDAR}/from/{start_date.strftime('%d-%m-%Y')}/to/{end_date.strftime('%d-%m-%Y')}"
    
    params = {
        "city": city,
        "country": country,
        "method": config.API_METHOD,
        "school": config.API_SCHOOL,
        "calendarMethod": "HJCoSA",
        "iso8601": "false",
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=config.API_TIMEOUT)
            
            if response.status_code == 429:
                raise PrayerAPIRateLimit("API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()

            # The API returns data in data.data array for each day
            for day_data in data.get("data", []):            
                greg_date_str = day_data["date"]["gregorian"]["date"]  # e.g. "01-02-2025"
                hijri_date_str = day_data['date']['hijri']['date'] # e.g. "01-02-1446"
                # Convert to datetime object
                date_obj = datetime.strptime(greg_date_str, "%d-%m-%Y").date()
                timings = day_data["timings"]
                
                # Convert timings to 24-hour format
                times = {
                    "Fajr": convert_to_24hr(clean_timezone_suffix(timings["Fajr"])),
                    "Dhuhr": convert_to_24hr(clean_timezone_suffix(timings["Dhuhr"])),
                    "Asr": convert_to_24hr(clean_timezone_suffix(timings["Asr"])),
                    "Maghrib": convert_to_24hr(clean_timezone_suffix(timings["Maghrib"])),
                    "Isha": convert_to_24hr(clean_timezone_suffix(timings["Isha"]))
                }
                # Store in DB
                store_prayer_times(date_obj, hijri_date_str, city, times)
            
            logger.info(f"Successfully stored prayer times for {city} between {start_date} and {end_date}")
            return True
            
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise PrayerAPIRateLimit(f"API rate limit exceeded: {e}")
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise PrayerAPIResponseError(f"API HTTP error: {e}")
            
        except requests.ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = config.API_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
            else:
                raise PrayerAPIConnectionError(f"Failed to connect after {max_retries} attempts: {e}")
                
        except requests.Timeout as e:
            logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = config.API_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
            else:
                raise PrayerAPIConnectionError(f"Request timeout after {max_retries} attempts: {e}")
                
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid API response format: {e}")
            raise PrayerAPIResponseError(f"Failed to parse API response: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error fetching prayer times range: {e}", exc_info=True)
            raise PrayerAPIException(f"Unexpected error: {e}")


def ensure_future_data(city, country="", days=None):
    """Ensure prayer times for the next 'days' days are available in DB.
    
    Args:
        city: City name
        country: Country name
        days: Number of days to prefetch (uses config.PREFETCH_DAYS if None)
        
    Returns:
        bool: True if data is available, False otherwise
    """
    if days is None:
        days = config.PREFETCH_DAYS
    
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    # Fetch existing data from DB
    existing = get_prayer_times_range_from_db(today, end_date, city)
    logger.debug(f"Database check for {city}: Found {len(existing)} dates between {today} and {end_date}")

    # Check which dates are missing
    missing_dates = []
    for i in range(days):
        date = today + timedelta(days=i)
        if date.strftime("%Y-%m-%d") not in existing:
            missing_dates.append(date)

    if not missing_dates:
        logger.info(f"All data present for {city} between {today} and {end_date}")
        return True

    logger.info(f"Missing {len(missing_dates)} dates for {city}. Fetching from {missing_dates[0]} to {missing_dates[-1]}")
    
    # Instead of fetching day-by-day, fetch all missing dates in one range if possible
    range_start = min(missing_dates)
    range_end = max(missing_dates)
    
    try:
        success = fetch_prayer_times_range(range_start, range_end, city, country)
        if success:
            logger.info(f"Successfully prefetched {len(missing_dates)} dates for {city}")
        return success
    except PrayerAPIConnectionError as e:
        logger.warning(f"Range fetch failed for {city}, falling back to individual fetches: {e}")
        # Fallback: fetch missing dates individually
        successful_count = 0
        for date in missing_dates:
            try:
                fetch_prayer_times_from_api(date, city, country)
                successful_count += 1
            except PrayerAPIException as e:
                logger.error(f"Failed to fetch {date} for {city}: {e}")
        logger.info(f"Prefetch fallback complete: {successful_count}/{len(missing_dates)} dates fetched")
        return successful_count > 0
    except PrayerAPIRateLimit:
        logger.error(f"API rate limit exceeded while fetching data for {city}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error ensuring future data: {e}", exc_info=True)
        return False


# =====================================================================
# GEOLOCATION
# =====================================================================

def get_location_from_ip():
    """Get user's location from IP address.
    
    Uses ipapi.co free service for geolocation without requiring API key.
    
    Returns:
        dict: {"city": str, "country": str} or None if detection fails
    """
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        response.raise_for_status()
        
        data = response.json()
        country = data.get('country_name', '')
        city = data.get('city', '')
        
        logger.info(f"IP Geolocation detected: {city}, {country}")
        return {"city": city, "country": country}
        
    except requests.exceptions.Timeout:
        logger.warning("IP geolocation timeout")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"IP geolocation request failed: {e}")
        return None
    except Exception as e:
        logger.warning(f"IP geolocation error: {e}")
        return None


def validate_location(location, country_cities):
    """Validate and sanitize location against available cities.
    
    Ensures the provided location matches an available country and city.
    Falls back to default if validation fails.
    
    Args:
        location (dict): {"city": str, "country": str} or None
        country_cities (dict): COUNTRY_CITIES reference with available locations
        
    Returns:
        dict: Validated {"city": str, "country": str} or default location
    """
    if not location:
        logger.debug("Location is None, returning default")
        return {"city": "Chicago", "country": "USA"}
    
    country = location.get("country", "").strip()
    city = location.get("city", "").strip()
    
    if country not in country_cities:
        logger.warning(f"Country '{country}' not supported, using default")
        return {"city": "Chicago", "country": "USA"}
    
    available_cities = country_cities[country]
    if city not in available_cities:
        logger.warning(f"City '{city}' not available in {country}, using first available city")
        return {"city": available_cities[0], "country": country}
    
    logger.info(f"Location validated: {city}, {country}")
    return {"city": city, "country": country}


def get_validated_location(country_cities):
    """Get location from IP and validate against available cities.
    
    Attempts to detect user's location from IP address and validates it
    against the configured list of available cities. Falls back to default
    if IP detection fails or detected city is not available.
    
    Args:
        country_cities (dict): COUNTRY_CITIES reference with available locations
        
    Returns:
        dict: Validated {"city": str, "country": str}
    """
    location = get_location_from_ip()
    validated = validate_location(location, country_cities)
    return validated


# =====================================================================
# UPDATE CHECKING (Linux/Raspberry Pi)
# =====================================================================

COOLDOWN_FILE = config.PROJECT_ROOT / ".update_cooldown"
COOLDOWN_SECONDS = 300  # 5 minutes


def check_for_updates():
    """Check if updates are available via git and run update script if found.
    
    Primarily intended for Linux/Raspberry Pi deployments.
    On Windows, it will skip as .sh scripts aren't natively supported.
    Includes cooldown to prevent restart loops if updates fail.
    """
    if platform.system() == "Windows":
        logger.debug("Auto-update check skipped on Windows.")
        return False

    # Check cooldown
    if COOLDOWN_FILE.exists():
        last_check = os.path.getmtime(COOLDOWN_FILE)
        if time.time() - last_check < COOLDOWN_SECONDS:
            logger.debug("Update check on cooldown. Skipping...")
            return False

    update_script = config.PROJECT_ROOT / "src" / "scripts" / "update_app.sh"
    
    if not update_script.exists():
        logger.warning(f"Update script not found at {update_script}")
        return False

    try:
        # Check for changes
        subprocess.run(["git", "fetch"], check=True, capture_output=True, cwd=config.PROJECT_ROOT, timeout=10)
        
        # Compare LOCAL vs REMOTE
        local = subprocess.check_output(["git", "rev-parse", "@"], cwd=config.PROJECT_ROOT, timeout=5).strip().decode('utf-8')
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=config.PROJECT_ROOT, timeout=5).strip().decode('utf-8')
        
        if local != remote:
            logger.info("Updates detected! Triggering update_app.sh...")
            COOLDOWN_FILE.touch()
            subprocess.Popen(["bash", str(update_script)], cwd=config.PROJECT_ROOT)
            return True
            
        logger.debug("No updates found.")
        return False
        
    except subprocess.TimeoutExpired:
        logger.error("Git commands timed out. Skipping update check.")
        return False
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return False
