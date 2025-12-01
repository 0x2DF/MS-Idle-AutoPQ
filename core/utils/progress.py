# progress.py
import time
from .logger import get_logger


class ProgressBar:
    """Simple progress bar for waits and retries."""
    
    def __init__(self, total, description="", width=30):
        self.total = total
        self.description = description
        self.width = width
        self.logger = get_logger()
    
    def show(self, current):
        """Show progress bar."""
        if self.total <= 0:
            return
        
        percent = min(100, int((current / self.total) * 100))
        filled = int((current / self.total) * self.width)
        bar = "█" * filled + "░" * (self.width - filled)
        
        self.logger.progress(f"  {self.description} [{bar}] {percent}%")
    
    def complete(self):
        """Clear the progress bar."""
        self.logger.clear_progress()


def wait_with_progress(duration, description="Waiting", check_stop=None):
    """
    Wait for duration seconds with a progress bar.
    
    Args:
        duration: Time to wait in seconds
        description: Description to show
        check_stop: Optional function that returns True if should stop
        
    Returns:
        bool: True if completed, False if interrupted
    """
    if duration <= 0:
        return True
    
    progress = ProgressBar(duration, description)
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed >= duration:
            progress.complete()
            return True
        
        if check_stop and check_stop():
            progress.complete()
            return False
        
        progress.show(elapsed)
        time.sleep(0.1)  # Update every 100ms
