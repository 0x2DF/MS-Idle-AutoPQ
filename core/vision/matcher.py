# matcher.py
import cv2
import numpy as np
from typing import Optional, List
from core.domain import Position
from core.utils import get_logger


class ImageMatcher:
    def __init__(self, debug, scale_range: Optional[List[float]] = None):
        """
        Initialize ImageMatcher with required dependencies.
        
        Args:
            debug: DebugManager instance for logging and visualization
            scale_range: List of scale factors to try (default: [0.5, 0.75, 1.0, 1.25, 1.5])
        """
        self.debug = debug
        self.scale_range = scale_range if scale_range is not None else [0.5, 0.75, 1.0, 1.25, 1.5]
        self.logger = get_logger()

    def find(self, screenshot, template_path, threshold=0.8) -> Optional[Position]:
        """
        Returns Position of match center or None if not found.
        Uses multi-scale template matching to handle different window sizes.
        
        Raises:
            TemplateNotFoundError: If template image file cannot be loaded
        """
        debug = self.debug
        
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            from core.exceptions import TemplateNotFoundError
            raise TemplateNotFoundError("image_matching", template_path)

        self.logger.verbose(f"Template: {template_path}, size: {template.shape}")
        self.logger.verbose(f"Screenshot size: {screenshot.shape}")

        # Convert to gray for speed
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Track best match across all scales
        best_match = None
        best_confidence = -1
        best_scale = 1.0
        best_location = None
        best_size = None

        # Try matching at different scales
        for scale in self.scale_range:
            # Resize template
            scaled_w = int(template_gray.shape[1] * scale)
            scaled_h = int(template_gray.shape[0] * scale)
            
            # Skip if scaled template is larger than screenshot
            if scaled_h > screenshot_gray.shape[0] or scaled_w > screenshot_gray.shape[1]:
                self.logger.verbose(f"Scale {scale:.2f}: Skipped (template too large)")
                continue
            
            scaled_template = cv2.resize(template_gray, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            self.logger.verbose(f"Scale {scale:.2f}: confidence {max_val:.3f}")
            
            # Track best match
            if max_val > best_confidence:
                best_confidence = max_val
                best_scale = scale
                best_location = max_loc
                best_size = (scaled_h, scaled_w)

        self.logger.debug(f"Best match: scale {best_scale:.2f}, confidence {best_confidence:.3f} (threshold: {threshold})")

        # Check if best match meets threshold
        if best_confidence < threshold:
            return None

        # Calculate center position
        h, w = best_size
        center_x = best_location[0] + w // 2
        center_y = best_location[1] + h // 2
        
        # Visualize the match region
        debug.show_match(screenshot, best_size, best_location, best_confidence, threshold)

        return Position(center_x, center_y)
