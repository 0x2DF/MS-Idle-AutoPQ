# actions.py
import pyautogui
from core.domain import Position
from .action_strategy import ActionRegistry


class ActionExecutor:
    """Executes actions using the strategy pattern."""
    
    def __init__(self, registry: ActionRegistry = None):
        """
        Initialize ActionExecutor.
        
        Args:
            registry: Optional ActionRegistry instance. If None, creates default registry.
        """
        pyautogui.FAILSAFE = False
        self.registry = registry if registry is not None else ActionRegistry()

    def run(self, action_name: str, pos: Position, offset: Position = None):
        """
        Execute an action at the given position.
        
        Args:
            action_name: Name of the action to execute
            pos: Position object in screen coords
            offset: Optional Position object for additional offset
            
        Raises:
            ValueError: If action_name is not registered
        """
        action = self.registry.get(action_name)
        try:
            action.execute(pos, offset)
        except Exception as e:
            # Catch and re-raise with more context
            print(f"[ActionExecutor] Error executing '{action_name}' at {pos}: {e}")
            raise
