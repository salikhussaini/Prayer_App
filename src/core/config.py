"""Centralized configuration and constants for Prayer App.

Defines all application constants, settings, and configuration values
in one place for easy maintenance and customization.
"""

from pathlib import Path

# ====================
# PROJECT PATHS
# ====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DATA_DIR / "prayer_times.db")
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE_PATH = LOGS_DIR / 'prayer_app.log'

# ====================
# LOGGING CONFIGURATION
# ====================
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_BACKUP_COUNT = 30  # Keep 30 days of logs
CONSOLE_LOG_LEVEL = "WARNING"  # Only show warnings+ in console

# ====================
# API CONFIGURATION
# ====================
API_URL_SINGLE = "https://api.aladhan.com/v1/timingsByCity"
API_URL_CALENDAR = "https://api.aladhan.com/v1/calendarByCity"

# Calculation Methods
# 2 = Islamic Society of North America (ISNA)
# 1 = University of Islamic Sciences, Karachi
# 3 = Muslim World League
# ... etc
API_CALCULATION_METHODS = {
    0: "Jafari / Shia Ithna-Ashari",
    1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America (ISNA)",
    3: "Muslim World League",
    4: "Umm Al-Qura University, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait",
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura, Singapore",
    12: "Union Organization islamic de France",
    13: "Diyanet İşleri Başkanlığı, Turkey",
    14: "Spiritual Administration of Muslims of Russia",
    15: "Moonsighting Committee Worldwide",
    16: "Dubai (experimental)",
    17: "Jabatan Kemajuan Islam Malaysia (JAKIM)",
    18: "Tunisia",
    19: "Algeria",
    20: "KEMENAG - Kementerian Agama Republik Indonesia",
    21: "Morocco",
    22: "Comunidade Islamica de Lisboa",
    23: "Ministry of Awqaf, Islamic Affairs and Holy Places, Jordan"
}

API_SCHOOLS = {
    0: "Shafi (Standard)",
    1: "Hanafi"
}

API_METHOD = 2  # Default: ISNA
API_SCHOOL = 1  # Default: Hanafi
API_TIMEOUT = 10  # seconds
API_MAX_RETRIES = 3
API_BACKOFF_BASE = 2  # Exponential backoff multiplier

# ====================
# PRAYER TIMES CONFIGURATION
# ====================
PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
PREFETCH_DAYS = 30  # Prefetch this many days ahead
ALERT_THRESHOLD_SECONDS = 30  # Alert when prayer is within this many seconds

# ====================
# DEFAULT LOCATION
# ====================
DEFAULT_COUNTRY = "USA"
DEFAULT_CITY = "Chicago"

# ====================
# UI CONFIGURATION
# ====================
FONT_SIZES = {
    "Small": {"clock": 60, "prayer_name": 14, "prayer_time": 28, "next_prayer": 24, "date": 30},
    "Medium": {"clock": 85, "prayer_name": 18, "prayer_time": 33, "next_prayer": 32, "date": 40},
    "Large": {"clock": 110, "prayer_name": 22, "prayer_time": 40, "next_prayer": 42, "date": 50},
}
DEFAULT_FONT_SIZE = "Medium"

# ====================
# UI COLORS
# ====================
class Colors:
    """Application color scheme."""
    BACKGROUND = "#000000"  # Black background
    PRIMARY = "#006853"  # Teal primary color
    ACCENT = "#00FF99"  # Bright green accent
    WARNING = "#FF5555"  # Red warning
    HIGHLIGHT = "#FFD700"  # Gold highlight
    HOUR_HAND = "#00FF99"  # Bright green
    SECOND_HAND = "#FF5555"  # Red

# ====================
# HIJRI MONTHS
# ====================
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

# ====================
# UI DIMENSIONS & TIMING
# ====================
AUTO_RESTART_DAYS = 7  # Automatically restart after this many days of uptime
SCREEN_WIDTH_FRACTION = 3  # Analog clock width = screen_width / 3
SCREEN_HEIGHT_FRACTION = 3  # Analog clock height = screen_height / 3
MIN_CLOCK_SIZE = 300  # Minimum analog clock size in pixels

# ====================
# AUDIO FILES
# ====================
AUDIO_FILES = {
    "athan": "src/assets/athan.wav",
    "fajr_athan": "src/assets/fajr_athan.wav",
    "dua": "src/assets/dua.wav",
}

# ====================
# ALERT SCHEDULING
# ====================
ALERT_CHECK_INTERVALS = [
    (15, 5000),      # Check every 5 seconds if within 15 seconds
    (60, 10000),     # Check every 10 seconds if within 1 minute
    (75, 20000),     # Check every 20 seconds if within 1.25 minutes
    (120, 30000),    # Check every 30 seconds if within 2 minutes
    (240, 60000),    # Check every 1 minute if within 4 minutes
    (600, 120000),   # Check every 2 minutes if within 10 minutes
    (900, 300000),   # Check every 5 minutes if within 15 minutes
    (1200, 600000),  # Check every 10 minutes if within 20 minutes
    (1800, 900000),  # Check every 15 minutes if within 30 minutes
    (3600, 1200000), # Check every 20 minutes if within 1 hour
    (7200, 2400000)  # Check every 40 minutes if within 2 hours
]

# Default 1 hour checks if no prayer is imminent
DEFAULT_ALERT_CHECK_INTERVAL = 6000000  # 1 hour
FALLBACK_ALERT_CHECK_INTERVAL = 12000000  # 2 hours (on error)

# ====================
# DATABASE CONFIGURATION
# ====================
DB_CHECK_SAME_THREAD = False  # Allow multi-threaded access
DB_TIMEOUT = 30  # Connection timeout in seconds
DB_BUSY_TIMEOUT = 5000  # Busy timeout in milliseconds
