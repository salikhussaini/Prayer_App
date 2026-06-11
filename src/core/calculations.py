from src.core.db import get_prayer_times_from_db, store_prayer_times
from src.core.api import fetch_prayer_times_from_api, ensure_future_data, PrayerAPIException
from src.core.logger_config import get_logger

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
