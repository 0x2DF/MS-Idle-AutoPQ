# loop.py
from core.constants import DEFAULT_BREAK_THRESHOLD, DEFAULT_ITERATION_DELAY


class Loop:
    """Represents a loop construct in a workflow."""
    
    def __init__(self, iterations, steps, break_on_find=None, 
                 break_threshold=DEFAULT_BREAK_THRESHOLD, 
                 iteration_delay=DEFAULT_ITERATION_DELAY):
        self.iterations = iterations
        self.steps = steps
        self.is_infinite = iterations == "infinite" or iterations == -1
        self.break_on_find = break_on_find
        self.break_threshold = break_threshold
        self.iteration_delay = iteration_delay
    
    def __repr__(self):
        iter_str = "infinite" if self.is_infinite else str(self.iterations)
        return f"Loop(iterations={iter_str}, steps={len(self.steps)})"
