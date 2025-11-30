# Input module - mouse and keyboard actions
from .actions import ActionExecutor
from .action_strategy import (
    ActionStrategy,
    ActionRegistry,
    ClickAction,
    DoubleClickAction,
    MoveAction,
    RightClickAction
)

__all__ = [
    'ActionExecutor',
    'ActionStrategy',
    'ActionRegistry',
    'ClickAction',
    'DoubleClickAction',
    'MoveAction',
    'RightClickAction'
]
