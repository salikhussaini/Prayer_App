"""
Helper functions for logging setup and prayer time calculations.
Combines logging configuration and business logic for prayer time retrieval.
"""

import logging
import logging.handlers
import time
from datetime import datetime

from src.core.config import LOGS_DIR, LOG_FILE_PATH, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOG_BACKUP_COUNT, CONSOLE_LOG_LEVEL
from src.core.db import get_prayer_times_from_db
from src.core.api import fetch_prayer_times_from_api, ensure_future_data, PrayerAPIException

_logging_initialized = False  # Prevent duplicate handler setup


# =====================================================================
# LOGGING SETUP
# =====================================================================

def setup_logging(level=logging.INFO):
    """Configure logging with daily rotating file handler.
    
    Args:
        level: Logging level (default: logging.INFO)
        
    Returns:
        logging.Logger: Configured root logger
        
    Log Format:
        %(asctime)s - %(name)s - %(levelname)s - %(message)s
        
    Behavior:
        - Creates daily rotating log files at midnight
        - Backup count: 30 days of logs retained
        - Log files stored in project data directory
        - Also logs to console for debugging
    """
    global _logging_initialized
    if _logging_initialized:
        return logging.getLogger()
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # Daily rotating file handler (rotates at midnight)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(LOG_FILE_PATH),
        when='midnight',  # Rotate at midnight
        interval=1,  # Every day
        backupCount=LOG_BACKUP_COUNT,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Set rotation filename format to include date
    file_handler.namer = lambda name: name.replace('.log', '') + '_' + \
        time.strftime('%Y-%m-%d', time.localtime()) + '.log'
    
    # Console handler for real-time feedback (only warnings and errors)
    console_level = logging.WARNING
    if CONSOLE_LOG_LEVEL == "INFO":
        console_level = logging.INFO
    elif CONSOLE_LOG_LEVEL == "DEBUG":
        console_level = logging.DEBUG
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    _logging_initialized = True
    
    # Log startup message
    root_logger.info(f"Logging initialized. Log files stored in: {LOGS_DIR}")
    
    return root_logger


def get_logger(name):
    """Get a logger instance for a specific module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        logging.Logger: Logger for the specified module
    """
    return logging.getLogger(name)


# =====================================================================
# PRAYER TIMES CALCULATION
# =====================================================================

logger = get_logger(__name__)


def calculate_prayer_times(date, location):
    """Calculate prayer times for a given date and location.
    
    Args:
        date: datetime.date object
        location: dict with 'city' and 'country' keys
        
    Returns:
        dict: Prayer times in {'Prayer': 'HH:MM'} format
        
    Raises:
        Exception: If prayer times cannot be calculated
    """
    city = location.get("city", "")
    country = location.get("country", "")
    
    # Try DB first
    times = get_prayer_times_from_db(date, city)

    if times:
        logger.debug(f"Found prayer times for {city} in database for {date}")
        return times

    logger.info(f"No data found for {city}, {country} on {date}. Attempting to fetch...")
    try:
        ensure_future_data(city=city, country=country, days=7)
        # Try DB again after prefetch
        times = get_prayer_times_from_db(date, city)
        if times:
            logger.info(f"Successfully fetched prayer times for {city}, {country} on {date}")
            return times
        else:
            # As fallback, call API just in case (rare scenario)
            logger.warning(f"Data not found after prefetch for {city}. Attempting direct API call...")
            times = fetch_prayer_times_from_api(date, city, country)
            return times
    except PrayerAPIException as e:
        logger.error(f"API error fetching prayer times for {city}, {country} on {date}: {e}")
        raise Exception(f"Failed to fetch prayer times for {city}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calculating prayer times: {e}", exc_info=True)
        raise Exception(f"Failed to calculate prayer times: {str(e)}")
