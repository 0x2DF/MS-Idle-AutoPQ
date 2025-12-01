# execution_context.py
import time
from core.constants import STOP_CHECK_INTERVAL
from core.utils import get_logger, wait_with_progress
from ..utils import CoordinateTransformer


class ExecutionContext:
    """Encapsulates the execution state and shared resources for workflow execution."""
    
    def __init__(self, capture, matcher, actions, debug, stop_event=None):
        self.capture = capture
        self.matcher = matcher
        self.actions = actions
        self.debug = debug
        self.stop_event = stop_event
        self.recovery_attempts = 0
        self.coordinate_transformer = CoordinateTransformer(capture)
        self.logger = get_logger()
    
    def is_stopped(self):
        """Check if execution should stop."""
        return self.stop_event and self.stop_event.is_set()
    
    def sleep(self, duration):
        """
        Sleep for duration seconds, checking stop event periodically.
        Returns True if sleep completed, False if interrupted.
        """
        if duration <= 0:
            return True
        
        # Use progress bar for waits
        return wait_with_progress(
            duration, 
            description=f"Waiting {duration:.1f}s",
            check_stop=lambda: self.stop_event and self.stop_event.is_set()
        )
    
    def find_and_execute_step(self, step):
        """
        Find the target and execute the action for a step.
        
        This method encapsulates the logic of finding a template, calculating
        coordinates, and executing the action. This follows "Tell, Don't Ask"
        by having the context do the work rather than exposing internals.
        
        Args:
            step: Step object to execute
            
        Returns:
            bool: True if target was found and action executed, False otherwise
        """
        # Capture frame
        frame = self.capture.grab(step.roi)
        self.logger.verbose(f"Captured frame shape: {frame.shape}")
        self.debug.show_frame("Captured Frame", frame)
        
        # Find target
        relative_pos = self.matcher.find(frame, step.find, step.threshold)
        
        if not relative_pos:
            return False
        
        # Found the target
        self.logger.debug(f"  ✓ Found at {relative_pos}")
        self.logger.verbose(f"  → ROI: {step.roi}, Offset: {step.offset}")
        
        # Calculate global position and execute action
        global_pos = self.calculate_screen_position(relative_pos, step.roi)
        self.logger.verbose(f"Global position (before offset): {global_pos}")
        
        final_pos = self.coordinate_transformer.apply_offset(global_pos, step.offset)
        self.logger.verbose(f"Final click position: {final_pos}")
        
        # Ensure window is active before executing action (for window capture mode)
        if hasattr(self.capture.strategy, 'ensure_window_active'):
            self.capture.strategy.ensure_window_active()
        
        # Execute action
        self.actions.run(step.action, global_pos, step.offset)
        
        return True
    
    def calculate_screen_position(self, relative_pos, roi):
        """
        Calculate screen position from relative position and ROI.
        
        Args:
            relative_pos: Position relative to captured region
            roi: Region of Interest used for capture
            
        Returns:
            Position in global screen coordinates
        """
        return self.coordinate_transformer.to_global_position(relative_pos, roi)
    
    def verify_template_absent(self, step):
        """
        Verify that a template is no longer present (state has changed).
        
        Args:
            step: Step object with template and verification settings
            
        Returns:
            bool: True if template is absent, False if still present
        """
        for verify_attempt in range(step.verify_retries):
            if not self.sleep(step.verify_delay):
                return False
            
            if self.is_stopped():
                return False
            
            frame = self.capture.grab(step.roi)
            pos = self.matcher.find(frame, step.find, step.threshold)
            
            if pos is None:
                self.logger.debug(f"  ✓ State changed (verified in {verify_attempt + 1}/{step.verify_retries} attempts)")
                return True
            
            if verify_attempt < step.verify_retries - 1:
                self.logger.debug(f"  → Verifying state change ({verify_attempt + 1}/{step.verify_retries})...")
        
        self.logger.debug(f"  ✗ State unchanged after {step.verify_retries} attempts")
        return False
