# printer.py


class WorkflowPrinter:
    """Handles all workflow output and step information printing."""
    
    def __init__(self, loop_states):
        """
        Initialize WorkflowPrinter.
        
        Args:
            loop_states: Dict mapping loop_id to loop metadata
        """
        self.loop_states = loop_states
    
    def print_step_info(self, step, loop_id, current_index, total_steps):
        """
        Print information about the current step.
        
        Args:
            step: Step object being executed
            loop_id: ID of the loop (None if not in a loop)
            current_index: Current step index
            total_steps: Total number of steps in workflow
        """
        if loop_id:
            self._print_loop_step_info(step, loop_id, current_index)
        else:
            self._print_regular_step_info(step, current_index, total_steps)
    
    def _print_loop_step_info(self, step, loop_id, current_index):
        """Print information for a step within a loop."""
        loop_state = self.loop_states[loop_id]
        loop = loop_state['loop']
        step_num = current_index - loop_state['start'] + 1
        total_steps = loop_state['end'] - loop_state['start'] + 1
        
        # Print loop iteration header at start of loop
        if current_index == loop_state['start']:
            if loop.is_infinite:
                print(f"[Workflow] Loop iteration {loop_state['iteration'] + 1} (infinite)")
            else:
                print(f"[Workflow] Loop iteration {loop_state['iteration'] + 1}/{loop.iterations}")
        
        print(f"  [Loop Step {step_num}/{total_steps}] {step.name}")
    
    def _print_regular_step_info(self, step, current_index, total_steps):
        """Print information for a regular (non-loop) step."""
        print(f"[Workflow] Step {current_index + 1}/{total_steps}: {step.name}")
