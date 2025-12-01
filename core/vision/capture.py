# capture.py
import mss
import numpy as np
import threading
from typing import Optional, Dict
from core.domain import Region, Position
from core.constants import WINDOW_REFRESH_INTERVAL


class CaptureStrategy:
    """Abstract base for capture strategies."""
    
    def get_monitor_region(self, roi: Optional[Region] = None) -> Dict[str, int]:
        """
        Get the monitor region to capture.
        Returns a dict with keys: left, top, width, height
        """
        raise NotImplementedError
    
    def get_offset(self) -> Position:
        """
        Get the screen offset for coordinate transformation.
        Returns Position offset to add to relative coordinates.
        """
        return Position(0, 0)


class FullScreenCaptureStrategy(CaptureStrategy):
    """Captures the full primary screen."""
    
    def __init__(self):
        """Initialize with thread-local mss screen capture instance."""
        self._local = threading.local()
    
    def _get_mss(self):
        """Get or create thread-local mss instance."""
        if not hasattr(self._local, 'mss_instance'):
            self._local.mss_instance = mss.mss()
        return self._local.mss_instance
    
    def get_monitor_region(self, roi: Optional[Region] = None) -> Dict[str, int]:
        if roi:
            return roi.to_monitor_dict()
        return self._get_mss().monitors[1]  # primary display


class WindowCaptureStrategy(CaptureStrategy):
    """Captures a specific window."""
    
    def __init__(self, window_manager, window_name, debug):
        """
        Initialize WindowCaptureStrategy with required dependencies.
        
        Args:
            window_manager: WindowManager instance for window operations
            window_name: Name of the window to capture
            debug: DebugManager instance for logging
        """
        self._local = threading.local()
        self.window_manager = window_manager
        self.window_name = window_name
        self._window_region: Optional[Region] = None
        self._last_check = 0
        self.debug = debug
    
    def refresh_window_region(self):
        """Force refresh of window region. Useful before critical operations."""
        import time
        self._window_region = self.window_manager.get_window_rect(self.window_name)
        self._last_check = time.time()
        
        if self._window_region is None:
            from core.exceptions import WindowNotFoundError
            raise WindowNotFoundError(self.window_name)
        
        self.debug.log(f"Window region refreshed: {self._window_region}")
        return self._window_region
    
    def _get_mss(self):
        """Get or create thread-local mss instance."""
        if not hasattr(self._local, 'mss_instance'):
            self._local.mss_instance = mss.mss()
        return self._local.mss_instance
    
    def get_monitor_region(self, roi: Optional[Region] = None) -> Dict[str, int]:
        import time
        
        debug = self.debug
        
        # Refresh window position periodically
        current_time = time.time()
        if self._window_region is None or (current_time - self._last_check) > WINDOW_REFRESH_INTERVAL:
            self._window_region = self.window_manager.get_window_rect(self.window_name)
            self._last_check = current_time
            
            if self._window_region is None:
                from core.exceptions import WindowNotFoundError
                raise WindowNotFoundError(self.window_name)
            
            debug.log(f"Window client rect: {self._window_region}")
        
        if roi:
            # ROI is relative to window
            region = {
                "left": self._window_region.x + roi.x,
                "top": self._window_region.y + roi.y,
                "width": roi.width,
                "height": roi.height
            }
            debug.log(f"Capture region (with ROI): {region}")
            return region
        
        region = self._window_region.to_monitor_dict()
        debug.log(f"Capture region (full window): {region}")
        return region
    
    def get_offset(self) -> Position:
        """Return the window's screen offset."""
        if self._window_region is None:
            return Position(0, 0)
        return Position(self._window_region.x, self._window_region.y)
    
    def ensure_window_active(self):
        """Ensure the target window is active and in foreground."""
        if hasattr(self.window_manager, 'bring_to_foreground'):
            return self.window_manager.bring_to_foreground(self.window_name)
        return True


class ScreenCapture:
    def __init__(self, strategy=None):
        """
        Initialize ScreenCapture with a capture strategy.
        
        Args:
            strategy: CaptureStrategy instance. If None, uses FullScreenCaptureStrategy.
        """
        self.strategy = strategy or FullScreenCaptureStrategy()
        self._local = threading.local()
    
    def _get_mss(self):
        """Get or create thread-local mss instance."""
        if not hasattr(self._local, 'mss_instance'):
            self._local.mss_instance = mss.mss()
        return self._local.mss_instance

    def grab(self, roi: Optional[Region] = None):
        """
        Capture screen region.
        
        Args:
            roi: Optional Region object to capture specific area
            
        Returns:
            numpy BGR image array
        """
        monitor = self.strategy.get_monitor_region(roi)
        img = np.array(self._get_mss().grab(monitor))
        return img[:, :, :3]  # drop alpha channel
    
    def get_offset(self) -> Position:
        """Get the coordinate offset from the capture strategy."""
        return self.strategy.get_offset()
