# logger.py
import sys
from enum import Enum


class LogLevel(Enum):
    """Log levels for controlling output verbosity."""
    QUIET = 0      # Only critical errors
    INFO = 1       # User-facing information (default)
    DEBUG = 2      # Detailed debugging information
    VERBOSE = 3    # Everything including internal details


class Logger:
    """Centralized logging with configurable verbosity levels."""
    
    def __init__(self, level=LogLevel.INFO):
        self.level = level
    
    def set_level(self, level):
        """Set the logging level."""
        self.level = level
    
    def info(self, message):
        """Log user-facing information (always shown unless QUIET)."""
        if self.level.value >= LogLevel.INFO.value:
            print(message)
    
    def debug(self, message):
        """Log debugging information (shown in DEBUG and VERBOSE modes)."""
        if self.level.value >= LogLevel.DEBUG.value:
            print(f"[DEBUG] {message}")
    
    def verbose(self, message):
        """Log verbose internal details (shown only in VERBOSE mode)."""
        if self.level.value >= LogLevel.VERBOSE.value:
            print(f"[VERBOSE] {message}")
    
    def error(self, message):
        """Log errors (always shown)."""
        print(f"[ERROR] {message}", file=sys.stderr)
    
    def progress(self, message, end='\r'):
        """Show progress information (overwrites same line)."""
        if self.level.value >= LogLevel.INFO.value:
            print(f"\r{message}", end=end, flush=True)
    
    def clear_progress(self):
        """Clear the progress line."""
        if self.level.value >= LogLevel.INFO.value:
            print("\r" + " " * 80 + "\r", end='', flush=True)


# Global logger instance
_logger = Logger()


def get_logger():
    """Get the global logger instance."""
    return _logger


def set_log_level(level):
    """Set the global logging level."""
    _logger.set_level(level)
