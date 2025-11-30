# execution_context.py
import time
from core.constants import STOP_CHECK_INTERVAL
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
    
    def is_stopped(self):
        """Check if execution should stop."""
        return self.stop_event and self.stop_event.is_set()
    
    def sleep(self, duration):
        """
        Sleep for duration seconds, checking stop event periodically.
        Returns True if sleep completed, False if interrupted.
        """
        if not self.stop_event:
            time.sleep(duration)
            return True
        
        # Check periodically for stop signal
        elapsed = 0
        while elapsed < duration:
            if self.stop_event.is_set():
                return False
            sleep_time = min(STOP_CHECK_INTERVAL, duration - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
        
        return True
    
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
        self.debug.log(f"Captured frame shape: {frame.shape}")
        self.debug.show_frame("Captured Frame", frame)
        
        # Find target
        relative_pos = self.matcher.find(frame, step.find, step.threshold)
        
        if not relative_pos:
            return False
        
        # Found the target
        print(f"  → Found {step.name} at relative position: {relative_pos}")
        self.debug.log(f"ROI: {step.roi}")
        self.debug.log(f"Offset: {step.offset}")
        
        # Calculate global position and execute action
        global_pos = self.calculate_screen_position(relative_pos, step.roi)
        self.debug.log(f"Global position (before offset): {global_pos}")
        
        final_pos = self.coordinate_transformer.apply_offset(global_pos, step.offset)
        self.debug.log(f"Final click position: {final_pos}")
        
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
                print(f"  → State change verified (attempt {verify_attempt + 1}/{step.verify_retries})")
                return True
            
            if verify_attempt < step.verify_retries - 1:
                print(f"  → State unchanged (attempt {verify_attempt + 1}/{step.verify_retries}), waiting...")
        
        print(f"  → State verification failed after {step.verify_retries} attempts")
        return False
