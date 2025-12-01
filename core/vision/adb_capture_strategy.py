# adb_capture_strategy.py
"""
Capture strategy that uses ADB screencap instead of window capture.
This ensures coordinates match perfectly between vision and ADB input.
"""

import numpy as np
import cv2
import tempfile
import os
from typing import Optional, Dict
from core.domain import Region, Position
from .capture import CaptureStrategy


class ADBCaptureStrategy(CaptureStrategy):
    """Captures screen directly from Android device via ADB."""
    
    def __init__(self, adb_client, debug=None):
        """
        Initialize ADB capture strategy.
        
        Args:
            adb_client: ADBClient instance
            debug: Optional DebugManager instance
        """
        self.adb = adb_client
        self.debug = debug
        self._device_size = None
        
        # Get device size once
        width, height = self.adb.get_screen_size()
        self._device_size = (width, height)
        
        if debug:
            debug.log(f"ADB capture initialized: {width}x{height}")
    
    def get_monitor_region(self, roi: Optional[Region] = None) -> Dict[str, int]:
        """
        Get the region to capture. For ADB, this is just metadata
        since we capture via screencap command.
        
        Returns a dict with keys: left, top, width, height
        """
        if roi:
            return {
                "left": roi.x,
                "top": roi.y,
                "width": roi.width,
                "height": roi.height
            }
        
        return {
            "left": 0,
            "top": 0,
            "width": self._device_size[0],
            "height": self._device_size[1]
        }
    
    def get_offset(self) -> Position:
        """
        Get the screen offset. For ADB capture, there's no offset
        since we're capturing directly from the device.
        """
        return Position(0, 0)
    
    def capture_screen(self) -> np.ndarray:
        """
        Capture screen from Android device via ADB.
        
        Returns:
            numpy BGR image array
        """
        # Use exec-out to get raw binary PNG data (not text)
        cmd = self.adb._build_command("exec-out", "screencap", "-p")
        
        import subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"ADB screencap failed: {result.stderr}")
        
        # result.stdout is already bytes (binary PNG data)
        nparr = np.frombuffer(result.stdout, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise RuntimeError("Failed to decode ADB screenshot")
        
        return img


class ADBScreenCapture:
    """
    Screen capture that uses ADB screencap.
    Coordinates from vision matching will directly correspond to ADB tap coordinates.
    """
    
    def __init__(self, adb_client, debug=None):
        """
        Initialize ADB screen capture.
        
        Args:
            adb_client: ADBClient instance
            debug: Optional DebugManager instance
        """
        self.strategy = ADBCaptureStrategy(adb_client, debug)
        self.adb = adb_client
    
    def grab(self, roi: Optional[Region] = None):
        """
        Capture screen from device.
        
        Args:
            roi: Optional Region object to capture specific area (crops after capture)
            
        Returns:
            numpy BGR image array
        """
        img = self.strategy.capture_screen()
        
        # Crop if ROI specified
        if roi:
            y1, y2 = roi.y, roi.y + roi.height
            x1, x2 = roi.x, roi.x + roi.width
            img = img[y1:y2, x1:x2]
        
        return img
    
    def get_offset(self) -> Position:
        """Get coordinate offset (always 0,0 for ADB capture)."""
        return Position(0, 0)
