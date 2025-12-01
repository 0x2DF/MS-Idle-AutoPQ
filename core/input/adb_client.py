# adb_client.py
import subprocess
import re
from typing import Optional, Tuple
from core.utils import get_logger


class ADBClient:
    """Client for interacting with Android devices via ADB."""
    
    def __init__(self, device_id: Optional[str] = None, adb_path: Optional[str] = None):
        """
        Initialize ADB client.
        
        Args:
            device_id: Optional device ID. If None, uses first available device.
            adb_path: Optional path to adb executable. If None, uses system ADB or bundled ADB.
        """
        self.device_id = device_id
        self._screen_size = None
        self.logger = get_logger()
        self.adb_path = self._find_adb(adb_path)
        self._verify_adb()
        
    def _find_adb(self, adb_path):
        """Find ADB executable."""
        if adb_path:
            return adb_path
        
        # Check for bundled ADB
        import os
        bundled_adb = os.path.join("tools", "adb", "adb.exe")
        if os.path.exists(bundled_adb):
            self.logger.debug(f"Using bundled ADB: {bundled_adb}")
            return bundled_adb
        
        # Use system ADB
        return "adb"
    
    def _verify_adb(self):
        """Verify ADB is installed and accessible."""
        try:
            result = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("ADB is not accessible")
            self.logger.verbose(f"ADB version: {result.stdout.split()[4]}")
        except FileNotFoundError:
            raise RuntimeError(
                f"ADB not found at: {self.adb_path}\n"
                "Run 'python setup_adb.py' to download ADB automatically."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to verify ADB: {e}")
    
    def _build_command(self, *args):
        """Build ADB command with device ID if specified."""
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        return cmd
    
    def execute(self, *args, timeout=10) -> subprocess.CompletedProcess:
        """
        Execute an ADB command.
        
        Args:
            *args: Command arguments
            timeout: Command timeout in seconds
            
        Returns:
            CompletedProcess instance
        """
        cmd = self._build_command(*args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {' '.join(cmd)}")
            raise
        except Exception as e:
            self.logger.error(f"ADB command failed: {' '.join(cmd)}")
            raise
    
    def tap(self, x: int, y: int):
        """
        Tap at screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        result = self.execute("shell", "input", "tap", str(x), str(y))
        if result.returncode != 0:
            self.logger.error(f"ADB tap failed: {result.stderr}")
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 100):
        """
        Swipe from one point to another.
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in milliseconds
        """
        result = self.execute(
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        )
        if result.returncode != 0:
            self.logger.error(f"ADB swipe failed: {result.stderr}")
    
    def text(self, text: str):
        """
        Input text (spaces must be escaped as %s).
        
        Args:
            text: Text to input
        """
        # Escape spaces for ADB
        escaped_text = text.replace(" ", "%s")
        result = self.execute("shell", "input", "text", escaped_text)
        if result.returncode != 0:
            self.logger.error(f"ADB text input failed: {result.stderr}")
    
    def keyevent(self, keycode: int):
        """
        Send a key event.
        
        Args:
            keycode: Android keycode (e.g., 4 for BACK, 3 for HOME)
        """
        result = self.execute("shell", "input", "keyevent", str(keycode))
        if result.returncode != 0:
            self.logger.error(f"ADB keyevent failed: {result.stderr}")
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get device screen size.
        
        Returns:
            Tuple of (width, height)
        """
        if self._screen_size:
            return self._screen_size
            
        result = self.execute("shell", "wm", "size")
        if result.returncode == 0:
            # Parse output like "Physical size: 1920x1080" or "Override size: 1920x1080"
            # Try to find any pattern with numbers
            lines = result.stdout.strip().split('\n')
            for line in lines:
                match = re.search(r'(\d+)x(\d+)', line)
                if match:
                    width, height = int(match.group(1)), int(match.group(2))
                    self._screen_size = (width, height)
                    self.logger.debug(f"Device screen size: {width}x{height}")
                    return self._screen_size
        
        # Try alternative method using dumpsys
        self.logger.debug("Trying alternative method to detect screen size...")
        result = self.execute("shell", "dumpsys", "window", "displays", timeout=5)
        if result.returncode == 0:
            # Look for patterns like "init=1920x1080" or "cur=1920x1080"
            match = re.search(r'(?:init|cur)=(\d+)x(\d+)', result.stdout)
            if match:
                width, height = int(match.group(1)), int(match.group(2))
                self._screen_size = (width, height)
                self.logger.debug(f"Device screen size (via dumpsys): {width}x{height}")
                return self._screen_size
        
        self.logger.error("Could not detect screen size, using default 1920x1080")
        self.logger.error("You may need to manually configure screen size if clicks are off")
        self._screen_size = (1920, 1080)
        return self._screen_size
    
    def list_devices(self) -> list:
        """
        List connected devices.
        
        Returns:
            List of device IDs
        """
        result = self.execute("devices")
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line.split()[0] for line in lines if line.strip() and 'device' in line]
            return devices
        return []
    
    def is_connected(self) -> bool:
        """Check if device is connected."""
        devices = self.list_devices()
        if self.device_id:
            return self.device_id in devices
        return len(devices) > 0
