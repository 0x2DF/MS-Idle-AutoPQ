# step_builder.py
from typing import Optional
from core.domain import Region, Position
from core.constants import (
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_END_DELAY,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRIES,
    DEFAULT_START_DELAY,
    DEFAULT_VERIFY_DELAY,
    DEFAULT_VERIFY_RETRIES
)
from ..models import Step


class StepBuilder:
    """
    Builder for creating Step objects with a fluent interface.
    Provides sensible defaults and validation logic.
    """
    
    def __init__(self):
        """Initialize builder with default values."""
        self._name = None
        self._find = None
        self._action = "click"
        self._threshold = DEFAULT_MATCH_THRESHOLD
        self._end_delay = DEFAULT_END_DELAY
        self._roi = None
        self._offset = Position(0, 0)
        self._retries = DEFAULT_RETRIES
        self._retry_delay = DEFAULT_RETRY_DELAY
        self._start_delay = DEFAULT_START_DELAY
        self._verify_state_change = False
        self._verify_delay = DEFAULT_VERIFY_DELAY
        self._verify_retries = DEFAULT_VERIFY_RETRIES
    
    def with_name(self, name: str):
        """Set the step name."""
        self._name = name
        return self
    
    def with_find(self, find: str):
        """Set the template to find."""
        self._find = find
        return self
    
    def with_action(self, action: str):
        """Set the action to perform."""
        self._action = action
        return self
    
    def with_threshold(self, threshold: float):
        """Set the match threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        self._threshold = threshold
        return self
    
    def with_end_delay(self, delay: float):
        """Set the delay after step execution."""
        if delay < 0:
            raise ValueError(f"End delay must be non-negative, got {delay}")
        self._end_delay = delay
        return self
    
    def with_roi(self, x: int, y: int, width: int, height: int):
        """Set the region of interest."""
        if width <= 0 or height <= 0:
            raise ValueError(f"ROI dimensions must be positive, got width={width}, height={height}")
        self._roi = Region(x, y, width, height)
        return self
    
    def with_roi_from_list(self, roi_data):
        """Set ROI from a list/tuple [x, y, width, height]."""
        if roi_data is None:
            self._roi = None
            return self
        
        if not isinstance(roi_data, (list, tuple)) or len(roi_data) != 4:
            raise ValueError(f"ROI must be a list/tuple of 4 integers [x, y, width, height], got {roi_data}")
        
        return self.with_roi(roi_data[0], roi_data[1], roi_data[2], roi_data[3])
    
    def with_offset(self, x: int, y: int):
        """Set the position offset."""
        self._offset = Position(x, y)
        return self
    
    def with_offset_from_list(self, offset_data):
        """Set offset from a list/tuple [x, y]."""
        if offset_data is None:
            self._offset = Position(0, 0)
            return self
        
        if not isinstance(offset_data, (list, tuple)) or len(offset_data) != 2:
            raise ValueError(f"Offset must be a list/tuple of 2 integers [x, y], got {offset_data}")
        
        return self.with_offset(offset_data[0], offset_data[1])
    
    def with_retries(self, retries: int):
        """Set the number of retries."""
        if retries < 0:
            raise ValueError(f"Retries must be non-negative, got {retries}")
        self._retries = retries
        return self
    
    def with_retry_delay(self, delay: float):
        """Set the delay between retries."""
        if delay < 0:
            raise ValueError(f"Retry delay must be non-negative, got {delay}")
        self._retry_delay = delay
        return self
    
    def with_start_delay(self, delay: float):
        """Set the delay before step execution."""
        if delay < 0:
            raise ValueError(f"Start delay must be non-negative, got {delay}")
        self._start_delay = delay
        return self
    
    def with_verify_state_change(self, verify: bool = True):
        """Enable/disable state change verification."""
        self._verify_state_change = verify
        return self
    
    def with_verify_delay(self, delay: float):
        """Set the delay for verification."""
        if delay < 0:
            raise ValueError(f"Verify delay must be non-negative, got {delay}")
        self._verify_delay = delay
        return self
    
    def with_verify_retries(self, retries: int):
        """Set the number of verification retries."""
        if retries < 0:
            raise ValueError(f"Verify retries must be non-negative, got {retries}")
        self._verify_retries = retries
        return self
    
    def from_dict(self, data: dict):
        """
        Populate builder from a dictionary (e.g., from YAML).
        
        Args:
            data: Dictionary containing step configuration
            
        Returns:
            self for chaining
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise ValueError(f"Step data must be a dictionary, got {type(data).__name__}")
        
        # Required fields
        if "name" not in data:
            raise ValueError("Step is missing required 'name' field")
        if "find" not in data:
            raise ValueError(f"Step '{data.get('name', 'unknown')}' is missing required 'find' field")
        
        self.with_name(data["name"])
        self.with_find(data["find"])
        
        # Optional fields with defaults
        if "action" in data:
            self.with_action(data["action"])
        if "threshold" in data:
            self.with_threshold(data["threshold"])
        if "end_delay" in data:
            self.with_end_delay(data["end_delay"])
        if "roi" in data:
            self.with_roi_from_list(data["roi"])
        if "offset" in data:
            self.with_offset_from_list(data["offset"])
        if "retries" in data:
            self.with_retries(data["retries"])
        if "retry_delay" in data:
            self.with_retry_delay(data["retry_delay"])
        if "start_delay" in data:
            self.with_start_delay(data["start_delay"])
        if "verify_state_change" in data:
            self.with_verify_state_change(data["verify_state_change"])
        if "verify_delay" in data:
            self.with_verify_delay(data["verify_delay"])
        if "verify_retries" in data:
            self.with_verify_retries(data["verify_retries"])
        
        return self
    
    def build(self) -> Step:
        """
        Build and return the Step object.
        
        Returns:
            Step instance
            
        Raises:
            ValueError: If required fields are not set
        """
        if self._name is None:
            raise ValueError("Step name is required")
        if self._find is None:
            raise ValueError("Step find template is required")
        
        return Step(
            name=self._name,
            find=self._find,
            action=self._action,
            threshold=self._threshold,
            end_delay=self._end_delay,
            roi=self._roi,
            offset=self._offset,
            retries=self._retries,
            retry_delay=self._retry_delay,
            start_delay=self._start_delay,
            verify_state_change=self._verify_state_change,
            verify_delay=self._verify_delay,
            verify_retries=self._verify_retries
        )
    
    @staticmethod
    def create_from_dict(data: dict) -> Step:
        """
        Convenience method to create a Step from a dictionary in one call.
        
        Args:
            data: Dictionary containing step configuration
            
        Returns:
            Step instance
        """
        return StepBuilder().from_dict(data).build()
