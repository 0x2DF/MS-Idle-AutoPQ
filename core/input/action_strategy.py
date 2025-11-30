# action_strategy.py
from abc import ABC, abstractmethod
import pyautogui
from core.domain import Position


class ActionStrategy(ABC):
    """Abstract base class for action strategies."""
    
    @abstractmethod
    def execute(self, position: Position, offset: Position = None):
        """
        Execute the action at the given position.
        
        Args:
            position: Position object in screen coords
            offset: Optional Position object for additional offset
        """
        pass
    
    def _calculate_final_position(self, position: Position, offset: Position = None):
        """Helper to calculate final position with offset."""
        if offset is None:
            offset = Position(0, 0)
        final_pos = position.offset(offset.x, offset.y)
        return final_pos.x, final_pos.y


class ClickAction(ActionStrategy):
    """Strategy for single click action."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        pyautogui.click(x, y)


class DoubleClickAction(ActionStrategy):
    """Strategy for double click action."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        pyautogui.doubleClick(x, y)


class MoveAction(ActionStrategy):
    """Strategy for mouse move action."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        pyautogui.moveTo(x, y)


class RightClickAction(ActionStrategy):
    """Strategy for right click action."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        pyautogui.rightClick(x, y)


class ActionRegistry:
    """Registry for managing action strategies."""
    
    def __init__(self):
        self._actions = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register the default set of actions."""
        self.register("click", ClickAction())
        self.register("double_click", DoubleClickAction())
        self.register("move", MoveAction())
        self.register("right_click", RightClickAction())
    
    def register(self, name: str, action: ActionStrategy):
        """
        Register a new action strategy.
        
        Args:
            name: Name of the action
            action: ActionStrategy instance
        """
        self._actions[name] = action
    
    def get(self, name: str) -> ActionStrategy:
        """
        Get an action strategy by name.
        
        Args:
            name: Name of the action
            
        Returns:
            ActionStrategy instance
            
        Raises:
            UnknownActionError: If action name is not registered
        """
        if name not in self._actions:
            from core.exceptions import UnknownActionError
            raise UnknownActionError(name)
        return self._actions[name]
    
    def has_action(self, name: str) -> bool:
        """Check if an action is registered."""
        return name in self._actions
