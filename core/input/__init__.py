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

# ADB-based actions
from .adb_actions import ADBActionExecutor
from .adb_client import ADBClient
from .adb_action_strategy import (
    ADBActionStrategy,
    ADBActionRegistry,
    ADBClickAction,
    ADBDoubleClickAction,
    ADBMoveAction,
    ADBLongPressAction,
    ADBSwipeAction
)

# Win32-based actions (no cursor movement)
try:
    from .win32_input import Win32ActionExecutor
    _has_win32 = True
except ImportError:
    _has_win32 = False
    Win32ActionExecutor = None

__all__ = [
    'ActionExecutor',
    'ActionStrategy',
    'ActionRegistry',
    'ClickAction',
    'DoubleClickAction',
    'MoveAction',
    'RightClickAction',
    # ADB
    'ADBActionExecutor',
    'ADBClient',
    'ADBActionStrategy',
    'ADBActionRegistry',
    'ADBClickAction',
    'ADBDoubleClickAction',
    'ADBMoveAction',
    'ADBLongPressAction',
    'ADBSwipeAction',
    # Win32
    'Win32ActionExecutor'
]
