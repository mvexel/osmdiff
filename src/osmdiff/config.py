"""Configuration settings for the osmdiff package."""

# Default API URLs and settings
API_CONFIG = {
    "overpass": {
        "base_url": "https://overpass-api.de/api",
        "timeout": 30,  # Default timeout in seconds
    },
    "osm": {
        "base_url": "https://api.openstreetmap.org/api/0.6",
        "timeout": 30,
    },
    "nominatim": {
        "base_url": "https://nominatim.openstreetmap.org",
        "timeout": 30,
    }
}

# Default values for AugmentedDiff
AUGMENTED_DIFF_CONFIG = {
    "minlon": None,
    "minlat": None,
    "maxlon": None,
    "maxlat": None,
    "timestamp": None
}

# User agent settings
USER_AGENT = "osmdiff/1.0"  # Replace with your actual user agent

# Common request headers
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/xml"
} 