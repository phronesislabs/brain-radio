"""Constants for Brain-Radio API."""

# Token and session durations (in seconds)
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour
SESSION_DURATION_SECONDS = 3600 * 24 * 7  # 7 days
OAUTH_STATE_EXPIRY_SECONDS = 600  # 10 minutes

# Spotify OAuth scopes
SPOTIFY_SCOPES = (
    "user-read-playback-state user-modify-playback-state user-read-currently-playing streaming"
)
