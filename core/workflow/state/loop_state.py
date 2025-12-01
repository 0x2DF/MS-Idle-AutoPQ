# loop_state.py
from core.utils import get_logger


class LoopStateManager:
    """Manages loop state and determines next execution index."""
    
    def __init__(self, loop_states, context):
        """
        Initialize LoopStateManager.
        
        Args:
            loop_states: Dict mapping loop_id to loop metadata
            context: ExecutionContext for checking break conditions
        """
        self.loop_states = loop_states
        self.context = context
        self.logger = get_logger()
    
    def get_next_index(self, current_index, loop_id, flattened_steps_count):
        """
        Determine the next step index based on loop state.
        
        Args:
            current_index: Current step index
            loop_id: ID of the loop (None if not in a loop)
            flattened_steps_count: Total number of flattened steps
            
        Returns:
            int or None: Next step index, or None if workflow should stop
        """
        if not loop_id:
            return current_index + 1
        
        loop_state = self.loop_states[loop_id]
        loop = loop_state['loop']
        
        # Check break condition before continuing
        if self._should_break_loop(loop):
            self.logger.info(f"  ⏹ Break condition met")
            return loop_state['end'] + 1
        
        # If not at end of loop, continue to next step
        if current_index < loop_state['end']:
            return current_index + 1
        
        # At end of loop, increment iteration
        loop_state['iteration'] += 1
        
        # Check if loop is complete
        if not loop.is_infinite and loop_state['iteration'] >= loop.iterations:
            return loop_state['end'] + 1
        
        # Handle iteration delay
        if loop.iteration_delay > 0:
            if not self.context.sleep(loop.iteration_delay):
                return None
        
        # Check break condition after delay
        if self._should_break_loop(loop):
            self.logger.info(f"  ⏹ Break condition met")
            return loop_state['end'] + 1
        
        # Loop back to start
        return loop_state['start']
    
    def _should_break_loop(self, loop):
        """
        Check if loop should break based on break condition.
        
        Args:
            loop: Loop object to check
            
        Returns:
            bool: True if loop should break, False otherwise
        """
        if not loop.break_on_find:
            return False
        frame = self.context.capture.grab()
        pos = self.context.matcher.find(frame, loop.break_on_find, loop.break_threshold)
        return pos is not None
