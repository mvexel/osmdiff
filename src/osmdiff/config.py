"""
Configuration settings for the osmdiff package.

This module contains all the configuration settings for the osmdiff package's API interactions.
It provides default values for API endpoints, timeouts, and request headers.

Configuration Structure:
    - API_CONFIG: Contains settings for different API endpoints (Overpass, OSM, Nominatim)
    - AUGMENTED_DIFF_CONFIG: Default parameters for AugmentedDiff operations
    - DEFAULT_HEADERS: Standard HTTP headers used across all API requests

Example:
    from osmdiff.config import API_CONFIG, DEFAULT_HEADERS

    # Get OSM API base URL
    osm_url = API_CONFIG["osm"]["base_url"]

    # Use default headers in requests
    response = requests.get(url, headers=DEFAULT_HEADERS)
"""

# Default API URLs and settings for different services
API_CONFIG = {
    "overpass": {
        "base_url": "https://adiffs.osmcha.org/changesets/{sequence}.adiff",
        "timeout": 30,  # Default timeout in seconds
    },
    "osm": {
        "base_url": "https://api.openstreetmap.org/api/0.6",
        "timeout": 30,
    },
    "nominatim": {
        "base_url": "https://nominatim.openstreetmap.org",
        "timeout": 30,
    },
}

# Default parameters for AugmentedDiff operations
AUGMENTED_DIFF_CONFIG = {
    "minlon": None,  # Minimum longitude for bounding box
    "minlat": None,  # Minimum latitude for bounding box
    "maxlon": None,  # Maximum longitude for bounding box
    "maxlat": None,  # Maximum latitude for bounding box
    "timestamp": None,  # Timestamp for diff operations
}

# User agent string following OSM API guidelines
# https://operations.osmfoundation.org/policies/api/
USER_AGENT = "osmdiff/1.0"  # Replace with your actual user agent

# Standard headers used in all API requests
DEFAULT_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json, text/xml"}
