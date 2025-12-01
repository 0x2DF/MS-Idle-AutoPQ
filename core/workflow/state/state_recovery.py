# state_recovery.py
from core.constants import MAX_RECOVERY_ATTEMPTS
from core.exceptions import StateRecoveryError
from core.utils import get_logger


class StateRecovery:
    """Handles workflow state recovery by detecting current state."""
    
    def __init__(self, context, flattened_steps, max_attempts=MAX_RECOVERY_ATTEMPTS):
        self.context = context
        self.flattened_steps = flattened_steps
        self.max_attempts = max_attempts
        self.logger = get_logger()
    
    def attempt_recovery(self):
        """
        Scan all flattened steps to determine current state.
        Returns the index of the detected step, or None if no state detected.
        
        Note: Returns None for backward compatibility. Consider using
        attempt_recovery_strict() for new code which raises exceptions.
        """
        self.context.recovery_attempts += 1
        self.logger.info(f"🔍 Recovery attempt {self.context.recovery_attempts}/{self.max_attempts}")
        self.logger.debug(f"Scanning {len(self.flattened_steps)} steps...")
        
        if self.context.recovery_attempts > self.max_attempts:
            return None
        
        detected_indices = []
        
        for index, step_info in enumerate(self.flattened_steps):
            step = step_info['step']
            self.logger.debug(f"  → Checking {index + 1}: {step.name}")
            
            frame = self.context.capture.grab(step.roi)
            pos = self.context.matcher.find(frame, step.find, step.threshold)
            
            if pos:
                detected_indices.append(index)
                self.logger.debug(f"    ✓ Found")
        
        if not detected_indices:
            self.logger.info(f"  ✗ No matching state found")
            return None
        
        best_index = max(detected_indices)
        best_step = self.flattened_steps[best_index]['step']
        self.logger.info(f"  ✓ Recovered to: {best_step.name} (step {best_index + 1})")
        
        return best_index
    
    def attempt_recovery_strict(self):
        """
        Scan all flattened steps to determine current state.
        Raises exception instead of returning None on failure.
        
        Returns:
            int: Index of the detected step
            
        Raises:
            StateRecoveryError: If recovery fails or max attempts exceeded
        """
        result = self.attempt_recovery()
        
        if result is None:
            if self.context.recovery_attempts > self.max_attempts:
                raise StateRecoveryError(self.context.recovery_attempts, self.max_attempts)
            else:
                raise StateRecoveryError(self.context.recovery_attempts, self.max_attempts)
        
        return result
    

