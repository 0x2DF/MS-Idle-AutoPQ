"""Application-wide constants."""

# Recovery settings
MAX_RECOVERY_ATTEMPTS = 5

# Execution timing
STOP_CHECK_INTERVAL = 0.1  # seconds between stop signal checks
LOOP_ITERATION_DELAY = 2  # seconds between loop iterations in controller

# Window capture settings
WINDOW_REFRESH_INTERVAL = 2  # seconds between window position refreshes

# Default step settings
DEFAULT_MATCH_THRESHOLD = 0.7
DEFAULT_END_DELAY = 1  # seconds
DEFAULT_RETRY_DELAY = 1  # seconds
DEFAULT_RETRIES = 10
DEFAULT_START_DELAY = 0  # seconds
DEFAULT_VERIFY_DELAY = 1  # seconds
DEFAULT_VERIFY_RETRIES = 3

# Default loop settings
DEFAULT_BREAK_THRESHOLD = 0.8
DEFAULT_ITERATION_DELAY = 0  # seconds
