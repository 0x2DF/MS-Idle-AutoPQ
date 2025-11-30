# step.py
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


class Step:
    def __init__(self, name: str, find: str, action: str, 
                 threshold: float = DEFAULT_MATCH_THRESHOLD, 
                 end_delay: float = DEFAULT_END_DELAY, 
                 roi: Optional[Region] = None, 
                 offset: Position = None, 
                 retries: int = DEFAULT_RETRIES, 
                 retry_delay: float = DEFAULT_RETRY_DELAY, 
                 start_delay: float = DEFAULT_START_DELAY, 
                 verify_state_change: bool = False,
                 verify_delay: float = DEFAULT_VERIFY_DELAY, 
                 verify_retries: int = DEFAULT_VERIFY_RETRIES):
        """
        Initialize a Step object.
        
        Note: Direct constructor use is considered internal. For new code,
        prefer using StepBuilder for better readability and validation:
        
            step = StepBuilder()
                .with_name("Click Button")
                .with_find("button.png")
                .with_action("click")
                .build()
        
        Or from a dictionary:
        
            step = StepBuilder.create_from_dict(step_data)
        """
        self.name = name
        self.find = find
        self.action = action
        self.threshold = threshold
        self.end_delay = end_delay
        self.roi = roi
        self.offset = offset if offset is not None else Position(0, 0)
        self.retries = retries
        self.retry_delay = retry_delay
        self.start_delay = start_delay
        self.verify_state_change = verify_state_change
        self.verify_delay = verify_delay
        self.verify_retries = verify_retries

    def __repr__(self):
        return f"Step(name={self.name}, find={self.find}, action={self.action})"
