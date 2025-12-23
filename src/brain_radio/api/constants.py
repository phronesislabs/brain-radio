"""Constants for Brain-Radio API."""

# HTTP status codes
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

# Time constants (in seconds)
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 3600 * 24
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7

# Token and session durations (in seconds)
TOKEN_EXPIRY_SECONDS = SECONDS_PER_HOUR  # 1 hour
SESSION_DURATION_SECONDS = SECONDS_PER_HOUR * HOURS_PER_DAY * DAYS_PER_WEEK  # 7 days
OAUTH_STATE_EXPIRY_SECONDS = 600  # 10 minutes

# Default values
DEFAULT_DURATION_MINUTES = 60

# Spotify OAuth scopes
SPOTIFY_SCOPES = (
    "user-read-playback-state user-modify-playback-state user-read-currently-playing streaming"
)
