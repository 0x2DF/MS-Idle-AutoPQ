# step_executor.py
from core.utils import get_logger


class StepExecutor:
    """Handles execution of individual steps with retry logic."""
    
    def __init__(self, context):
        self.context = context
        self.logger = get_logger()
    
    def execute(self, step):
        """
        Execute a step with retry logic.
        Returns True if successful, False if all retries exhausted.
        """
        # Apply start delay
        if step.start_delay > 0:
            if not self.context.sleep(step.start_delay):
                return False
        
        # Try to execute with retries
        for attempt in range(step.retries):
            if self.context.is_stopped():
                return False
            
            # Show retry attempt if not first try
            if attempt > 0:
                self.logger.info(f"  → Retry {attempt}/{step.retries - 1}")
            
            if self._try_execute_once(step):
                return True
            
            # Check if stopped after failed attempt
            if self.context.is_stopped():
                return False
            
            # Wait before next retry
            if attempt < step.retries - 1:
                if not self.context.sleep(step.retry_delay):
                    return False
        
        return False
    
    def _try_execute_once(self, step):
        """
        Attempt to find and execute a step once.
        Returns True if successful, False otherwise.
        """
        # Tell the context to find and execute the step
        # This follows "Tell, Don't Ask" - we tell the context what to do
        # rather than asking for its internals and doing it ourselves
        if not self.context.find_and_execute_step(step):
            return False
        
        # Apply end delay
        if not self.context.sleep(step.end_delay):
            return False
        
        # Verify state change if enabled
        if step.verify_state_change:
            if self.context.verify_template_absent(step):
                return True
            else:
                return False
        
        return True
