# adb_action_strategy.py
from abc import ABC, abstractmethod
from core.domain import Position
from .adb_client import ADBClient


class ADBActionStrategy(ABC):
    """Abstract base class for ADB action strategies."""
    
    def __init__(self, adb_client: ADBClient):
        """
        Initialize with ADB client.
        
        Args:
            adb_client: ADBClient instance
        """
        self.adb = adb_client
    
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
        return int(final_pos.x), int(final_pos.y)


class ADBClickAction(ADBActionStrategy):
    """Strategy for single tap action via ADB."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        print(f"[ADB] Tap at coordinates: ({x}, {y})")
        self.adb.tap(x, y)


class ADBDoubleClickAction(ADBActionStrategy):
    """Strategy for double tap action via ADB."""
    
    def execute(self, position: Position, offset: Position = None):
        import time
        x, y = self._calculate_final_position(position, offset)
        print(f"[ADB] Double-tap at coordinates: ({x}, {y})")
        self.adb.tap(x, y)
        time.sleep(0.1)  # Small delay between taps
        self.adb.tap(x, y)


class ADBMoveAction(ADBActionStrategy):
    """Strategy for move action via ADB (no-op, as ADB doesn't have cursor)."""
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        print(f"[ADB] Move action (no-op): ({x}, {y})")
        # ADB doesn't have a cursor concept, so this is a no-op


class ADBLongPressAction(ADBActionStrategy):
    """Strategy for long press action via ADB (simulated with swipe)."""
    
    def __init__(self, adb_client: ADBClient, duration: int = 1000):
        """
        Initialize long press action.
        
        Args:
            adb_client: ADBClient instance
            duration: Long press duration in milliseconds
        """
        super().__init__(adb_client)
        self.duration = duration
    
    def execute(self, position: Position, offset: Position = None):
        x, y = self._calculate_final_position(position, offset)
        print(f"[ADB] Long-press at coordinates: ({x}, {y}) for {self.duration}ms")
        # Swipe from point to itself with duration simulates long press
        self.adb.swipe(x, y, x, y, self.duration)


class ADBSwipeAction(ADBActionStrategy):
    """Strategy for swipe action via ADB."""
    
    def __init__(self, adb_client: ADBClient, duration: int = 300):
        """
        Initialize swipe action.
        
        Args:
            adb_client: ADBClient instance
            duration: Swipe duration in milliseconds
        """
        super().__init__(adb_client)
        self.duration = duration
    
    def execute(self, position: Position, offset: Position = None):
        """
        Swipe from position to position+offset.
        
        Args:
            position: Start position
            offset: End offset (required for swipe)
        """
        if offset is None:
            print("[ADB] Warning: Swipe requires offset, using tap instead")
            self.adb.tap(int(position.x), int(position.y))
            return
        
        x1, y1 = int(position.x), int(position.y)
        x2, y2 = int(position.x + offset.x), int(position.y + offset.y)
        print(f"[ADB] Swipe from ({x1}, {y1}) to ({x2}, {y2})")
        self.adb.swipe(x1, y1, x2, y2, self.duration)


class ADBActionRegistry:
    """Registry for managing ADB action strategies."""
    
    def __init__(self, adb_client: ADBClient):
        """
        Initialize registry with ADB client.
        
        Args:
            adb_client: ADBClient instance
        """
        self.adb = adb_client
        self._actions = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register the default set of ADB actions."""
        self.register("click", ADBClickAction(self.adb))
        self.register("double_click", ADBDoubleClickAction(self.adb))
        self.register("move", ADBMoveAction(self.adb))
        self.register("right_click", ADBLongPressAction(self.adb))  # Map right-click to long press
        self.register("long_press", ADBLongPressAction(self.adb))
        self.register("swipe", ADBSwipeAction(self.adb))
    
    def register(self, name: str, action: ADBActionStrategy):
        """
        Register a new action strategy.
        
        Args:
            name: Name of the action
            action: ADBActionStrategy instance
        """
        self._actions[name] = action
    
    def get(self, name: str) -> ADBActionStrategy:
        """
        Get an action strategy by name.
        
        Args:
            name: Name of the action
            
        Returns:
            ADBActionStrategy instance
            
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
