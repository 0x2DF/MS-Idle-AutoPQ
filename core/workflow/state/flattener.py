# flattener.py
from ..models import Loop


class WorkflowFlattener:
    """Handles flattening of nested workflow structures into a linear execution list."""
    
    def flatten(self, items):
        """
        Flatten workflow items into a linear list with metadata.
        
        Args:
            items: List of workflow items (Steps and Loops)
            
        Returns:
            tuple: (flattened_steps, loop_states)
                - flattened_steps: List of dicts with 'step' and 'loop_id'
                - loop_states: Dict mapping loop_id to loop metadata
        """
        flattened = []
        loop_states = {}
        self._flatten_recursive(items, flattened, loop_states)
        return flattened, loop_states
    
    def _flatten_recursive(self, items, flattened, loop_states):
        """Recursively flatten workflow items."""
        for item in items:
            if isinstance(item, Loop):
                loop_id = id(item)
                loop_start = len(flattened)
                
                for step in item.steps:
                    if isinstance(step, Loop):
                        self._flatten_recursive([step], flattened, loop_states)
                    else:
                        flattened.append({'step': step, 'loop_id': loop_id})
                
                loop_end = len(flattened) - 1
                loop_states[loop_id] = {
                    'loop': item,
                    'start': loop_start,
                    'end': loop_end,
                    'iteration': 0
                }
            else:
                flattened.append({'step': item, 'loop_id': None})
