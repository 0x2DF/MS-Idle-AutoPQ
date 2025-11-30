# window_manager.py
import platform
from typing import Optional
from core.domain import Region


class WindowManager:
    """Abstract interface for window management operations."""
    
    def get_window_rect(self, window_name: str) -> Optional[Region]:
        """
        Get the bounding rectangle of a window by name.
        Returns Region or None if not found.
        """
        raise NotImplementedError


class WindowsWindowManager(WindowManager):
    """Windows-specific window manager using win32gui."""
    
    def __init__(self):
        try:
            import win32gui
            self.win32gui = win32gui
        except ImportError:
            raise ImportError("pywin32 is required for Windows window management. Install with: pip install pywin32")
    
    def get_window_rect(self, window_name: str) -> Optional[Region]:
        """Find window by name and return its client area rectangle in screen coordinates."""
        hwnd = self._find_window(window_name)
        if not hwnd:
            return None
        
        try:
            # Get client area dimensions
            client_rect = self.win32gui.GetClientRect(hwnd)
            # client_rect is (0, 0, right, bottom) - relative to window
            width = client_rect[2]
            height = client_rect[3]
            
            # Convert client area top-left to screen coordinates
            left, top = self.win32gui.ClientToScreen(hwnd, (0, 0))
            
            return Region(left, top, width, height)
        except Exception as e:
            print(f"[WindowManager] Error getting window rect: {e}")
            return None
    
    def bring_to_foreground(self, window_name: str) -> bool:
        """
        Bring window to foreground to ensure it's active.
        Returns True if successful, False otherwise.
        """
        hwnd = self._find_window(window_name)
        if not hwnd:
            return False
        
        try:
            # Restore if minimized
            if self.win32gui.IsIconic(hwnd):
                self.win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
            
            # Bring to foreground
            self.win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            print(f"[WindowManager] Error bringing window to foreground: {e}")
            return False
    
    def _find_window(self, window_name):
        """Find window handle by partial name match."""
        result = {"hwnd": None}
        
        def callback(hwnd, extra):
            try:
                if self.win32gui.IsWindowVisible(hwnd):
                    title = self.win32gui.GetWindowText(hwnd)
                    if window_name.lower() in title.lower():
                        result["hwnd"] = hwnd
                        return False  # Stop enumeration
            except Exception:
                # Skip windows that cause errors (invalid handles, etc.)
                pass
            return True
        
        try:
            self.win32gui.EnumWindows(callback, None)
        except Exception as e:
            # If EnumWindows fails entirely, log and return None
            print(f"[WindowManager] Warning: EnumWindows failed: {e}")
            return None
        
        return result["hwnd"]


class LinuxWindowManager(WindowManager):
    """Linux-specific window manager (placeholder for future implementation)."""
    
    def get_window_rect(self, window_name: str) -> Optional[Region]:
        raise NotImplementedError("Linux window management not yet implemented")


class MacWindowManager(WindowManager):
    """macOS-specific window manager (placeholder for future implementation)."""
    
    def get_window_rect(self, window_name: str) -> Optional[Region]:
        raise NotImplementedError("macOS window management not yet implemented")


def create_window_manager():
    """Factory function to create platform-specific window manager."""
    system = platform.system()
    
    if system == "Windows":
        return WindowsWindowManager()
    elif system == "Linux":
        return LinuxWindowManager()
    elif system == "Darwin":
        return MacWindowManager()
    else:
        raise NotImplementedError(f"Window management not supported on {system}")
