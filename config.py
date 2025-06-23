"""
Configuration settings for the Valorant Combo Checker
"""

# Rate limiting settings
DEFAULT_DELAY_BETWEEN_CHECKS = 2.0  # seconds
MIN_DELAY = 1.0  # minimum delay in seconds
MAX_DELAY = 10.0  # maximum delay in seconds

# Request settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# GUI settings
WINDOW_TITLE = "Valorant Account Combo Checker"
WINDOW_SIZE = "800x600"
WINDOW_MIN_SIZE = (600, 400)

# File settings
SUPPORTED_FILE_TYPES = [
    ("Text files", "*.txt"),
    ("CSV files", "*.csv"),
    ("All files", "*.*")
]

# Result export formats
EXPORT_FORMATS = [
    ("Text files", "*.txt"),
    ("CSV files", "*.csv")
]

# Logging settings
LOG_FILE = "combo_checker.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# Valorant authentication endpoints
VALORANT_AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
VALORANT_LOGIN_URL = "https://auth.riotgames.com/api/v1/authorization"

# Thread settings
MAX_CONCURRENT_CHECKS = 5
