# debug.py
import cv2
import os
from datetime import datetime


class DebugManager:
    """Centralized debug logging and visualization."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.debug_dir = "debug"
        if self.enabled:
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def log(self, message: str):
        """Print debug message if debugging is enabled."""
        if self.enabled:
            print(f"  [Debug] {message}")
    
    def show_frame(self, title: str, frame):
        """Save a frame to the debug directory if debugging is enabled."""
        if self.enabled:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{title.replace(' ', '_')}_{timestamp}.png"
            filepath = os.path.join(self.debug_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"  [Debug] Saved frame: {filepath}")
    
    def show_match(self, screenshot, template_shape, match_loc, confidence: float, threshold: float):
        """Visualize the match region with rectangle and confidence score, saved to debug directory."""
        if not self.enabled:
            return
        
        h, w = template_shape
        top_left = match_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center_x = match_loc[0] + w // 2
        center_y = match_loc[1] + h // 2
        
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, top_left, bottom_right, (0, 255, 0), 2)
        cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
        cv2.putText(debug_img, f"{confidence:.3f}", (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"match_{timestamp}.png"
        filepath = os.path.join(self.debug_dir, filename)
        cv2.imwrite(filepath, debug_img)
        print(f"  [Debug] Saved match visualization: {filepath}")
    
    def cleanup(self):
        """Clean up debug resources."""
        pass  # No windows to clean up since we're saving to files
