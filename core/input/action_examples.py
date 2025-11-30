# action_examples.py
"""
Example of how to extend the action system with custom actions.

This demonstrates the Open/Closed Principle - the system is open for extension
but closed for modification. New actions can be added without changing existing code.
"""

import pyautogui
from core.domain import Position
from .action_strategy import ActionStrategy, ActionRegistry


# Example: Custom action for triple click
class TripleClickAction(ActionStrategy):
    """Strategy for triple click action."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        pyautogui.click(x, y, clicks=3)


# Example: Custom action for drag
class DragAction(ActionStrategy):
    """Strategy for drag action (requires target position in offset)."""
    
    def execute(self, position: Position, offset: Position = None):
        start_x, start_y = position.x, position.y
        if offset:
            end_x, end_y = position.x + offset.x, position.y + offset.y
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y)


# Example: How to register custom actions
def register_custom_actions(registry: ActionRegistry):
    """Register custom actions to the registry."""
    registry.register("triple_click", TripleClickAction())
    registry.register("drag", DragAction())


# Example usage:
# registry = ActionRegistry()
# register_custom_actions(registry)
# executor = ActionExecutor(registry)
# executor.run("triple_click", Position(100, 100))
