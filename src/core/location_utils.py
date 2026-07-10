"""Location detection and validation utilities.

Provides IP-based geolocation with fallback to default location and validation
against available cities in the application.
"""

import requests
from src.core.logger_config import get_logger

logger = get_logger(__name__)


def get_location_from_ip():
    """
    Get user's location from IP address.
    
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
    """
    Validate and sanitize location against available cities.
    
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
    
    # Check if country exists in our list
    if country not in country_cities:
        logger.warning(f"Country '{country}' not supported, using default")
        return {"city": "Chicago", "country": "USA"}
    
    # Check if city exists for this country
    available_cities = country_cities[country]
    if city not in available_cities:
        logger.warning(f"City '{city}' not available in {country}, using first available city")
        return {"city": available_cities[0], "country": country}
    
    logger.info(f"Location validated: {city}, {country}")
    return {"city": city, "country": country}


def get_validated_location(country_cities):
    """
    Get location from IP and validate against available cities.
    
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
