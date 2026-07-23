"""
Core Backend Module for Prayer App
Combines configuration, database, API, and helper functions.
"""

import sqlite3
import requests
import logging
import logging.handlers
import time
import threading
import os
import subprocess
import platform
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta, date
import re
import json


# =====================================================================
# CONFIGURATION
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DATA_DIR / "prayer_times.db")
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE_PATH = LOGS_DIR / 'prayer_app.log'

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_BACKUP_COUNT = 30
CONSOLE_LOG_LEVEL = "WARNING"

# API Configuration
API_URL_SINGLE = "https://api.aladhan.com/v1/timingsByCity"
API_URL_CALENDAR = "https://api.aladhan.com/v1/calendarByCity"

API_CALCULATION_METHODS = {
    0: "Jafari / Shia Ithna-Ashari", 1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America (ISNA)", 3: "Muslim World League",
    4: "Umm Al-Qura University, Makkah", 5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran", 8: "Gulf Region",
    9: "Kuwait", 10: "Qatar", 11: "Majlis Ugama Islam Singapura, Singapore",
    12: "Union Organization islamic de France", 13: "Diyanet İşleri Başkanlığı, Turkey",
    14: "Spiritual Administration of Muslims of Russia", 15: "Moonsighting Committee Worldwide",
    16: "Dubai (experimental)", 17: "Jabatan Kemajuan Islam Malaysia (JAKIM)",
    18: "Tunisia", 19: "Algeria", 20: "KEMENAG - Kementerian Agama Republik Indonesia",
    21: "Morocco", 22: "Comunidade Islamica de Lisboa",
    23: "Ministry of Awqaf, Islamic Affairs and Holy Places, Jordan"
}

API_SCHOOLS = {0: "Shafi (Standard)", 1: "Hanafi"}

API_METHOD = 2
API_SCHOOL = 1
API_TIMEOUT = 10
API_MAX_RETRIES = 3
API_BACKOFF_BASE = 2

# Prayer Times
PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
PREFETCH_DAYS = 30
ALERT_THRESHOLD_SECONDS = 30

# Default Location
DEFAULT_COUNTRY = "USA"
DEFAULT_CITY = "Chicago"

# UI Configuration
FONT_SIZES = {
    "Small": {"clock": 85, "prayer_name": 18, "prayer_time": 33, "next_prayer": 32, "date": 40},
    "Medium": {"clock": 110, "prayer_name": 22, "prayer_time": 40, "next_prayer": 42, "date": 50},
    "Large": {"clock": 140, "prayer_name": 28, "prayer_time": 50, "next_prayer": 52, "date": 60}
}
DEFAULT_FONT_SIZE = "Medium"

# Window Configuration
DEFAULT_WINDOW_STATE = "windowed"  # Options: windowed, maximized, fullscreen
DEFAULT_START_MINIMIZED = False
DEFAULT_WINDOW_GEOMETRY = None  # Will be set at runtime

# Data Management
DEFAULT_DATA_RETENTION_DAYS = 30  # Automatically clean up data older than this

class Colors:
    BACKGROUND = "#000000"
    PRIMARY = "#006853"
    ACCENT = "#00FF99"
    WARNING = "#FF5555"
    HIGHLIGHT = "#FFD700"
    HOUR_HAND = "#00FF99"
    SECOND_HAND = "#FF5555"

HIJRI_MONTHS = {
    1: {"english": "Muharram", "arabic": "مُحَرَّم"},
    2: {"english": "Safar", "arabic": "صَفَر"},
    3: {"english": "Rabi' al-Awwal", "arabic": "رَبِيع ٱلْأَوَّل"},
    4: {"english": "Rabi' al-Thani", "arabic": "رَبِيع ٱلثَّانِي"},
    5: {"english": "Jumada al-Awwal", "arabic": "جُمَادَىٰ ٱلْأُولَىٰ"},
    6: {"english": "Jumada al-Thani", "arabic": "جُمَادَىٰ ٱلثَّانِيَة"},
    7: {"english": "Rajab", "arabic": "رَجَب"},
    8: {"english": "Sha'ban", "arabic": "شَعْبَان"},
    9: {"english": "Ramadan", "arabic": "رَمَضَان"},
    10: {"english": "Shawwal", "arabic": "شَوَّال"},
    11: {"english": "Dhu al-Qi'dah", "arabic": "ذُو ٱلْقِعْدَة"},
    12: {"english": "Dhu al-Hijjah", "arabic": "ذُو ٱلْحِجَّة"}
}

AUTO_RESTART_DAYS = 7
AUDIO_FILES = {
    "athan": "src/assets/athan.wav",
    "fajr_athan": "src/assets/fajr_athan.wav",
    "dua": "src/assets/dua.wav",
}


# =====================================================================
# LOGGING SETUP
# =====================================================================

_logging_initialized = False

def setup_logging(level=logging.INFO):
    """Configure logging with daily rotating file handler."""
    global _logging_initialized
    if _logging_initialized:
        return logging.getLogger()
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(LOG_FILE_PATH), when='midnight', interval=1,
        backupCount=LOG_BACKUP_COUNT, encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.namer = lambda name: name.replace('.log', '') + '_' + \
        time.strftime('%Y-%m-%d', time.localtime()) + '.log'
    
    console_level = logging.WARNING
    if CONSOLE_LOG_LEVEL == "INFO":
        console_level = logging.INFO
    elif CONSOLE_LOG_LEVEL == "DEBUG":
        console_level = logging.DEBUG
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    _logging_initialized = True
    root_logger.info(f"Logging initialized. Log files stored in: {LOGS_DIR}")
    
    return root_logger


def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


logger = get_logger(__name__)


# =====================================================================
# DATABASE OPERATIONS
# =====================================================================

class DatabaseManager:
    """Singleton database connection manager."""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute('PRAGMA journal_mode=WAL')
        return self._connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


_db_manager = DatabaseManager()


def init_db():
    """Initialize database and create tables."""
    with _db_manager.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prayer_times (
                date TEXT, hijri_date TEXT, city TEXT,
                fajr TEXT, dhuhr TEXT, asr TEXT, maghrib TEXT, isha TEXT,
                PRIMARY KEY (date, city)
            )
        """)


def store_prayer_times(date, hijri_date, city, times):
    """Store prayer times in database."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO prayer_times 
                (date, hijri_date, city, fajr, dhuhr, asr, maghrib, isha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date.strftime("%Y-%m-%d"), hijri_date, city,
                  times["Fajr"], times["Dhuhr"], times["Asr"],
                  times["Maghrib"], times["Isha"]))
    except KeyError as e:
        raise ValueError(f"Missing prayer time key: {e}")
    except Exception as e:
        raise Exception(f"Failed to store prayer times for {city} on {date}: {e}")


def get_prayer_times_from_db(date, city):
    """Retrieve prayer times for a specific date and city."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT fajr, dhuhr, asr, maghrib, isha, hijri_date 
                FROM prayer_times WHERE date=? AND city=?
            """, (date.strftime("%Y-%m-%d"), city))
            row = cursor.fetchone()
    except Exception as e:
        raise Exception(f"Failed to retrieve prayer times for {city}: {e}")
    
    if row:
        return {
            "Fajr": row[0], "Dhuhr": row[1], "Asr": row[2],
            "Maghrib": row[3], "Isha": row[4], "hijri_date": row[5]
        }
    return None


def get_prayer_times_range_from_db(start_date, end_date, city):
    """Retrieve prayer times for a date range."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute('''
                SELECT date, fajr, dhuhr, asr, maghrib, isha
                FROM prayer_times WHERE city = ? AND date BETWEEN ? AND ?
                ORDER BY date ASC
            ''', (city, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()
    except Exception as e:
        raise Exception(f"Failed to retrieve prayer times range for {city}: {e}")

    result = {}
    if rows:
        for row in rows:
            result[row[0]] = {
                "Fajr": row[1], "Dhuhr": row[2], "Asr": row[3],
                "Maghrib": row[4], "Isha": row[5]
            }
    return result


def cleanup_old_prayer_data(retention_days=DEFAULT_DATA_RETENTION_DAYS):
    """Delete prayer data older than retention_days."""
    try:
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d")
        
        with _db_manager.get_cursor() as cursor:
            cursor.execute("DELETE FROM prayer_times WHERE date < ?", (cutoff_date,))
            deleted_count = cursor.rowcount
        
        if deleted_count > 0:
            logger.info(f"✅ Cleaned up {deleted_count} old prayer records (older than {retention_days} days)")
        else:
            logger.debug(f"No old prayer records to clean (retention: {retention_days} days)")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up old prayer data: {e}")
        raise


def get_database_size():
    """Get current database size in MB."""
    try:
        db_path = Path(DB_PATH)
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
    return 0


def clear_all_prayer_data():
    """Completely clear all prayer data from database."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute("DELETE FROM prayer_times")
            deleted_count = cursor.rowcount
        
        logger.info(f"✅ Cleared all prayer data ({deleted_count} records deleted)")
        return deleted_count
    except Exception as e:
        logger.error(f"Error clearing prayer data: {e}")
        raise


def get_prayer_data_stats():
    """Get statistics about stored prayer data."""
    try:
        with _db_manager.get_cursor() as cursor:
            # Total records
            cursor.execute("SELECT COUNT(*) FROM prayer_times")
            total_records = cursor.fetchone()[0]
            
            # Unique cities
            cursor.execute("SELECT COUNT(DISTINCT city) FROM prayer_times")
            unique_cities = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM prayer_times")
            result = cursor.fetchone()
            earliest_date = result[0] if result[0] else "N/A"
            latest_date = result[1] if result[1] else "N/A"
        
        return {
            "total_records": total_records,
            "unique_cities": unique_cities,
            "earliest_date": earliest_date,
            "latest_date": latest_date,
            "database_size_mb": get_database_size()
        }
    except Exception as e:
        logger.error(f"Error getting prayer data stats: {e}")
        return {}


def schedule_periodic_cleanup(retention_days=DEFAULT_DATA_RETENTION_DAYS, check_interval_hours=24):
    """Schedule periodic cleanup of old prayer data.
    
    Args:
        retention_days: Days to keep data before deletion
        check_interval_hours: Hours between cleanup checks (default 24)
    
    Note: This runs in a daemon thread and will continue until app exits.
    """
    def cleanup_loop():
        logger.info(f"📋 Periodic cleanup scheduler started (runs every {check_interval_hours}h, keeps {retention_days}d)")
        while True:
            try:
                # Sleep for specified interval
                sleep_seconds = check_interval_hours * 3600
                time.sleep(sleep_seconds)
                
                # Run cleanup
                cleanup_old_prayer_data(retention_days)
            except Exception as e:
                logger.error(f"Error in periodic cleanup loop: {e}")
                # Continue the loop even on error
                time.sleep(60)
    
    # Start daemon thread for cleanup
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True, name="PrayerDataCleanupThread")
    cleanup_thread.start()
    logger.info("🧹 Prayer data periodic cleanup thread started")


# =====================================================================
# API EXCEPTIONS
# =====================================================================

class PrayerAPIException(Exception):
    """Base exception for prayer API errors."""
    pass

class PrayerAPIConnectionError(PrayerAPIException):
    """Connection to API failed."""
    pass

class PrayerAPIResponseError(PrayerAPIException):
    """Invalid or malformed API response."""
    pass

class PrayerAPIRateLimit(PrayerAPIException):
    """API rate limit exceeded."""
    pass


# =====================================================================
# API FUNCTIONS
# =====================================================================

def convert_to_24hr(time_str):
    """Convert prayer time to 24-hour format."""
    if not time_str or not isinstance(time_str, str):
        logger.warning(f"Invalid time string: {time_str}")
        return time_str
    
    time_str = time_str.strip()
    
    if ':' in time_str and not any(c.isalpha() for c in time_str):
        return time_str
    
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        logger.warning(f"Could not parse time string: {time_str}")
        return time_str


def clean_timezone_suffix(s):
    """Remove timezone suffix like '(CST)'."""
    return re.sub(r"\s*\(?[A-Z]{2,4}\)?\s*$", "", s).strip()


def fetch_prayer_times_from_api(date, city, country="", max_retries=None):
    """Fetch prayer times from API for a single date."""
    if max_retries is None:
        max_retries = API_MAX_RETRIES
    
    params = {
        "city": city, "country": country, "method": API_METHOD,
        "date": date.strftime("%d-%m-%Y"), "school": API_SCHOOL
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(API_URL_SINGLE, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 429:
                raise PrayerAPIRateLimit("API rate limit exceeded")
            
            response.raise_for_status()
            
            response_json = response.json()["data"]
            data = response_json["timings"]
            greg_date_str = response_json["date"]["gregorian"]["date"]
            hijri_date_str = response_json["date"]["hijri"]["date"]
            
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
                wait_time = API_BACKOFF_BASE ** attempt
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
    """Fetch prayer times for a date range."""
    if max_retries is None:
        max_retries = API_MAX_RETRIES
    
    url = f"{API_URL_CALENDAR}/from/{start_date.strftime('%d-%m-%Y')}/to/{end_date.strftime('%d-%m-%Y')}"
    
    params = {
        "city": city, "country": country, "method": API_METHOD,
        "school": API_SCHOOL, "calendarMethod": "HJCoSA", "iso8601": "false",
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 429:
                raise PrayerAPIRateLimit("API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()

            for day_data in data.get("data", []):            
                greg_date_str = day_data["date"]["gregorian"]["date"]
                hijri_date_str = day_data['date']['hijri']['date']
                date_obj = datetime.strptime(greg_date_str, "%d-%m-%Y").date()
                timings = day_data["timings"]
                
                times = {
                    "Fajr": convert_to_24hr(clean_timezone_suffix(timings["Fajr"])),
                    "Dhuhr": convert_to_24hr(clean_timezone_suffix(timings["Dhuhr"])),
                    "Asr": convert_to_24hr(clean_timezone_suffix(timings["Asr"])),
                    "Maghrib": convert_to_24hr(clean_timezone_suffix(timings["Maghrib"])),
                    "Isha": convert_to_24hr(clean_timezone_suffix(timings["Isha"]))
                }
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
                wait_time = API_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
            else:
                raise PrayerAPIConnectionError(f"Failed to connect after {max_retries} attempts: {e}")
                
        except requests.Timeout as e:
            logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = API_BACKOFF_BASE ** attempt
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
    """Ensure prayer times for the next N days are available."""
    if days is None:
        days = PREFETCH_DAYS
    
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    existing = get_prayer_times_range_from_db(today, end_date, city)
    logger.debug(f"Database check for {city}: Found {len(existing)} dates between {today} and {end_date}")

    missing_dates = []
    for i in range(days):
        date = today + timedelta(days=i)
        if date.strftime("%Y-%m-%d") not in existing:
            missing_dates.append(date)

    if not missing_dates:
        logger.info(f"All data present for {city} between {today} and {end_date}")
        return True

    logger.info(f"Missing {len(missing_dates)} dates for {city}. Fetching...")
    
    range_start = min(missing_dates)
    range_end = max(missing_dates)
    
    try:
        success = fetch_prayer_times_range(range_start, range_end, city, country)
        if success:
            logger.info(f"Successfully prefetched {len(missing_dates)} dates for {city}")
        return success
    except PrayerAPIConnectionError as e:
        logger.warning(f"Range fetch failed, fallback to individual fetches: {e}")
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


def get_location_from_ip():
    """Get user's location from IP address."""
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
    """Validate and sanitize location against available cities."""
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
        logger.warning(f"City '{city}' not available in {country}, using first available")
        return {"city": available_cities[0], "country": country}
    
    logger.info(f"Location validated: {city}, {country}")
    return {"city": city, "country": country}


def get_validated_location(country_cities):
    """Get location from IP and validate."""
    location = get_location_from_ip()
    validated = validate_location(location, country_cities)
    return validated


COOLDOWN_FILE = PROJECT_ROOT / ".update_cooldown"
COOLDOWN_SECONDS = 300


def check_for_updates():
    """Check if updates are available via git (Linux/Pi only)."""
    if platform.system() == "Windows":
        logger.debug("Auto-update check skipped on Windows.")
        return False

    if COOLDOWN_FILE.exists():
        last_check = os.path.getmtime(COOLDOWN_FILE)
        if time.time() - last_check < COOLDOWN_SECONDS:
            logger.debug("Update check on cooldown. Skipping...")
            return False

    update_script = PROJECT_ROOT / "src" / "scripts" / "update_app.sh"
    
    if not update_script.exists():
        logger.warning(f"Update script not found at {update_script}")
        return False

    try:
        subprocess.run(["git", "fetch"], check=True, capture_output=True, 
                      cwd=PROJECT_ROOT, timeout=10)
        
        local = subprocess.check_output(["git", "rev-parse", "@"], 
                                       cwd=PROJECT_ROOT, timeout=5).strip().decode('utf-8')
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"], 
                                        cwd=PROJECT_ROOT, timeout=5).strip().decode('utf-8')
        
        if local != remote:
            logger.info("Updates detected! Triggering update_app.sh...")
            COOLDOWN_FILE.touch()
            subprocess.Popen(["bash", str(update_script)], cwd=PROJECT_ROOT)
            return True
            
        logger.debug("No updates found.")
        return False
        
    except subprocess.TimeoutExpired:
        logger.error("Git commands timed out. Skipping update check.")
        return False
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return False


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def save_settings(settings):
    """Save settings to JSON file in data cache."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        logger.info(f"Settings saved to {SETTINGS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}", exc_info=True)


def load_settings():
    """Load settings from JSON cache, return defaults if not found."""
    # Define defaults
    defaults = {
        "country": DEFAULT_COUNTRY,
        "city": DEFAULT_CITY,
        "method": API_METHOD,
        "school": API_SCHOOL,
        "font_size": DEFAULT_FONT_SIZE,
        "volume": 1.0,
        "athan_file": str(PROJECT_ROOT / "src/assets/athan.wav"),
        "dua_file": str(PROJECT_ROOT / "src/assets/dua.wav"),
        "alert_threshold": ALERT_THRESHOLD_SECONDS,
        "prayer_alerts": {"Fajr": True, "Dhuhr": True, "Asr": True, "Maghrib": True, "Isha": True},
        "window_state": DEFAULT_WINDOW_STATE,
        "start_minimized": DEFAULT_START_MINIMIZED,
        "window_geometry": DEFAULT_WINDOW_GEOMETRY,
        "data_retention_days": DEFAULT_DATA_RETENTION_DAYS
    }
    
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            logger.info(f"Settings loaded from {SETTINGS_FILE}")
            # Merge with defaults to ensure all keys are present
            return {**defaults, **settings}
    except json.JSONDecodeError:
        logger.warning(f"Settings file corrupted, using defaults")
    except Exception as e:
        logger.warning(f"Failed to load settings: {e}, using defaults")
    
    # Return default settings
    return defaults


def calculate_prayer_times(date, location):
    """Calculate prayer times for a given date and location."""
    city = location.get("city", "")
    country = location.get("country", "")
    
    times = get_prayer_times_from_db(date, city)

    if times:
        logger.debug(f"Found prayer times for {city} in database for {date}")
        return times

    logger.info(f"No data found for {city}, {country} on {date}. Attempting to fetch...")
    try:
        ensure_future_data(city=city, country=country, days=7)
        times = get_prayer_times_from_db(date, city)
        if times:
            logger.info(f"Successfully fetched prayer times for {city}, {country} on {date}")
            return times
        else:
            logger.warning(f"Data not found after prefetch. Attempting direct API call...")
            times = fetch_prayer_times_from_api(date, city, country)
            return times
    except PrayerAPIException as e:
        logger.error(f"API error fetching prayer times for {city}, {country} on {date}: {e}")
        raise Exception(f"Failed to fetch prayer times for {city}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calculating prayer times: {e}", exc_info=True)
        raise Exception(f"Failed to calculate prayer times: {str(e)}")
