"""Constants for the Sporet integration."""

DOMAIN = "sporet"

# API Configuration
API_BASE_URL = "https://api.sporet.no/loypeapi/public/skiroutes"
API_SEGMENT_URL = "https://api.sporet.no/loypeapi/public/skisegments"
UPDATE_INTERVAL_SECONDS = 900  # 15 minutes

# Configuration Fields
CONF_BEARER_TOKEN = "bearer_token"
CONF_IS_SEGMENT = "is_segment"
CONF_SLOPE_ID = "slope_id"

# Attribution
ATTRIBUTION = "Data provided by Sporet.no"
