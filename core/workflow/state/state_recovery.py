# state_recovery.py
from core.constants import MAX_RECOVERY_ATTEMPTS
from core.exceptions import StateRecoveryError


class StateRecovery:
    """Handles workflow state recovery by detecting current state."""
    
    def __init__(self, context, flattened_steps, max_attempts=MAX_RECOVERY_ATTEMPTS):
        self.context = context
        self.flattened_steps = flattened_steps
        self.max_attempts = max_attempts
    
    def attempt_recovery(self):
        """
        Scan all flattened steps to determine current state.
        Returns the index of the detected step, or None if no state detected.
        
        Note: Returns None for backward compatibility. Consider using
        attempt_recovery_strict() for new code which raises exceptions.
        """
        self.context.recovery_attempts += 1
        print(f"[Recovery] Attempt {self.context.recovery_attempts}/{self.max_attempts}")
        print(f"[Recovery] Scanning {len(self.flattened_steps)} steps...")
        
        if self.context.recovery_attempts > self.max_attempts:
            return None
        
        detected_indices = []
        
        for index, step_info in enumerate(self.flattened_steps):
            step = step_info['step']
            print(f"  → Checking {index + 1}: {step.name}")
            
            frame = self.context.capture.grab(step.roi)
            pos = self.context.matcher.find(frame, step.find, step.threshold)
            
            if pos:
                detected_indices.append(index)
                print(f"    ✓ Found at {pos}")
        
        if not detected_indices:
            print(f"[Recovery] No matching state found")
            return None
        
        best_index = max(detected_indices)
        best_step = self.flattened_steps[best_index]['step']
        print(f"[Recovery] Selected: {best_step.name} (index {best_index + 1})")
        
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
    

