# matcher.py
import cv2
import numpy as np
from typing import Optional
from core.domain import Position


class ImageMatcher:
    def __init__(self, debug):
        """
        Initialize ImageMatcher with required dependencies.
        
        Args:
            debug: DebugManager instance for logging and visualization
        """
        self.debug = debug

    def find(self, screenshot, template_path, threshold=0.8) -> Optional[Position]:
        """
        Returns Position of match center or None if not found.
        
        Raises:
            TemplateNotFoundError: If template image file cannot be loaded
        """
        debug = self.debug
        
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            from core.exceptions import TemplateNotFoundError
            # Note: We don't have step_name here, so we use template_path as identifier
            raise TemplateNotFoundError("image_matching", template_path)

        debug.log(f"Template: {template_path}, size: {template.shape}")
        debug.log(f"Screenshot size: {screenshot.shape}")

        # Convert to gray for speed
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        debug.log(f"Match confidence: {max_val:.3f} (threshold: {threshold})")

        h, w = template_gray.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # Visualize the match region
        debug.show_match(screenshot, template_gray.shape, max_loc, max_val, threshold)

        if max_val < threshold:
            return None

        return Position(center_x, center_y)
