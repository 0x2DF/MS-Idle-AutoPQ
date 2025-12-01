# win32_input.py
"""
Windows-specific input using SendInput to send clicks to a specific window.
This doesn't move the physical cursor - it sends input directly to the window.
"""

import time
from ctypes import windll, Structure, c_long, c_ulong, sizeof, byref, POINTER
from core.domain import Position


# Windows constants
INPUT_MOUSE = 0
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Windows structures
class MOUSEINPUT(Structure):
    _fields_ = [
        ('dx', c_long),
        ('dy', c_long),
        ('mouseData', c_ulong),
        ('dwFlags', c_ulong),
        ('time', c_ulong),
        ('dwExtraInfo', POINTER(c_ulong))
    ]

class INPUT(Structure):
    _fields_ = [
        ('type', c_ulong),
        ('mi', MOUSEINPUT)
    ]


class Win32Input:
    """Send input to a specific window using Win32 API."""
    
    def __init__(self, window_manager, window_name):
        """
        Initialize Win32 input.
        
        Args:
            window_manager: WindowManager instance
            window_name: Name of target window
        """
        try:
            import win32gui
            import win32con
            self.win32gui = win32gui
            self.win32con = win32con
        except ImportError:
            raise ImportError("pywin32 required for Win32 input")
        
        self.window_manager = window_manager
        self.window_name = window_name
        self.user32 = windll.user32
        self._cached_hwnd = None
        
        # Find and cache the window handle on init
        self._cached_hwnd = self._find_window_safe()
        if not self._cached_hwnd:
            raise RuntimeError(f"Window not found: {self.window_name}")
        print(f"[Win32] Found window handle: {self._cached_hwnd}")
    
    def _find_window_safe(self):
        """Safely find window handle without EnumWindows."""
        try:
            # Try direct FindWindow first (faster and more reliable)
            hwnd = self.win32gui.FindWindow(None, self.window_name)
            if hwnd:
                return hwnd
            
            # Fall back to partial match
            return self.window_manager._find_window(self.window_name)
        except Exception as e:
            print(f"[Win32] Error finding window: {e}")
            return None
    
    def _get_hwnd(self):
        """Get window handle (uses cached value)."""
        # Verify cached handle is still valid
        if self._cached_hwnd:
            try:
                if self.win32gui.IsWindow(self._cached_hwnd):
                    return self._cached_hwnd
            except:
                pass
        
        # Re-find if invalid
        self._cached_hwnd = self._find_window_safe()
        if not self._cached_hwnd:
            raise RuntimeError(f"Window not found: {self.window_name}")
        return self._cached_hwnd
    
    def _screen_to_client(self, hwnd, screen_x, screen_y):
        """Convert screen coordinates to client coordinates."""
        # ScreenToClient expects a tuple (x, y) and returns (x, y)
        client_x, client_y = self.win32gui.ScreenToClient(hwnd, (screen_x, screen_y))
        return client_x, client_y
    
    def click(self, x, y):
        """
        Click at screen coordinates.
        Sends click directly to window without moving physical cursor.
        
        Args:
            x, y: Screen coordinates (will be converted to client coordinates)
        """
        hwnd = self._get_hwnd()
        
        # Convert screen coords to client coords
        client_x, client_y = self._screen_to_client(hwnd, x, y)
        
        # Pack coordinates into lParam (LOWORD = x, HIWORD = y)
        lParam = client_y << 16 | (client_x & 0xFFFF)
        
        # Try SendMessage first (synchronous, more reliable)
        method = "SendMessage"
        try:
            self.win32gui.SendMessage(
                hwnd,
                self.win32con.WM_LBUTTONDOWN,
                self.win32con.MK_LBUTTON,
                lParam
            )
            
            time.sleep(0.05)  # Small delay
            
            self.win32gui.SendMessage(
                hwnd,
                self.win32con.WM_LBUTTONUP,
                0,
                lParam
            )
        except Exception as e:
            # Fall back to PostMessage
            method = "PostMessage"
            print(f"[Win32] SendMessage failed ({e}), trying PostMessage")
            self.win32gui.PostMessage(
                hwnd,
                self.win32con.WM_LBUTTONDOWN,
                self.win32con.MK_LBUTTON,
                lParam
            )
            
            time.sleep(0.05)
            
            self.win32gui.PostMessage(
                hwnd,
                self.win32con.WM_LBUTTONUP,
                0,
                lParam
            )
        
        print(f"[Win32] {method} at client ({client_x}, {client_y})")
    
    def double_click(self, x, y):
        """Double click at coordinates."""
        self.click(x, y)
        time.sleep(0.1)
        self.click(x, y)
    
    def right_click(self, x, y):
        """Right click at coordinates."""
        hwnd = self._get_hwnd()
        client_x, client_y = self._screen_to_client(hwnd, x, y)
        lParam = (client_y << 16) | (client_x & 0xFFFF)
        
        self.win32gui.PostMessage(hwnd, self.win32con.WM_RBUTTONDOWN, self.win32con.MK_RBUTTON, lParam)
        time.sleep(0.05)
        self.win32gui.PostMessage(hwnd, self.win32con.WM_RBUTTONUP, 0, lParam)
        
        print(f"[Win32] Right-clicked at screen ({x}, {y}) -> client ({client_x}, {client_y})")


class Win32ActionExecutor:
    """Action executor using Win32 PostMessage (no cursor movement)."""
    
    def __init__(self, window_manager, window_name):
        """
        Initialize Win32 action executor.
        
        Args:
            window_manager: WindowManager instance
            window_name: Name of target window
        """
        self.win32_input = Win32Input(window_manager, window_name)
        print(f"[Win32] Initialized for window: {window_name}")
        print("[Win32] Using PostMessage (cursor will not move)")
    
    def run(self, action_name: str, pos: Position, offset: Position = None):
        """
        Execute an action at the given position.
        
        Args:
            action_name: Name of the action (click, double_click, right_click, move)
            pos: Position in screen coordinates
            offset: Optional offset
        """
        # Calculate final position
        final_x = pos.x
        final_y = pos.y
        if offset:
            final_x += offset.x
            final_y += offset.y
        
        # Execute action
        if action_name == "click":
            self.win32_input.click(final_x, final_y)
        elif action_name == "double_click":
            self.win32_input.double_click(final_x, final_y)
        elif action_name == "right_click":
            self.win32_input.right_click(final_x, final_y)
        elif action_name == "move":
            # Move is a no-op for Win32 (no cursor to move)
            print(f"[Win32] Move action (no-op): ({final_x}, {final_y})")
        else:
            from core.exceptions import UnknownActionError
            raise UnknownActionError(action_name)
