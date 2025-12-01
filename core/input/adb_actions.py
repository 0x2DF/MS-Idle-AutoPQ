# adb_actions.py
from core.domain import Position
from .adb_client import ADBClient
from .adb_action_strategy import ADBActionRegistry


class ADBActionExecutor:
    """
    Executes actions using ADB instead of pyautogui.
    
    When used with ADBScreenCapture, coordinates from vision matching
    will directly correspond to ADB tap coordinates (no translation needed).
    """
    
    def __init__(self, device_id: str = None, registry: ADBActionRegistry = None):
        """
        Initialize ADB ActionExecutor.
        
        Args:
            device_id: Optional ADB device ID. If None, uses first available device.
            registry: Optional ADBActionRegistry instance. If None, creates default registry.
        """
        self.adb = ADBClient(device_id=device_id)
        
        # Verify device is connected
        if not self.adb.is_connected():
            devices = self.adb.list_devices()
            if not devices:
                raise RuntimeError(
                    "No ADB devices connected. Please ensure your emulator/device is running.\n"
                    "For BlueStacks, enable ADB in Settings > Advanced > Android Debug Bridge"
                )
            print(f"[ADB] Available devices: {devices}")
        
        # Get screen size for reference
        width, height = self.adb.get_screen_size()
        print(f"[ADB] Connected to device with screen size: {width}x{height}")
        
        self.registry = registry if registry is not None else ADBActionRegistry(self.adb)

    def run(self, action_name: str, pos: Position, offset: Position = None):
        """
        Execute an action at the given position.
        
        Args:
            action_name: Name of the action to execute
            pos: Position object (device coordinates when using ADBScreenCapture)
            offset: Optional Position object for additional offset
            
        Raises:
            ValueError: If action_name is not registered
        """
        action = self.registry.get(action_name)
        try:
            action.execute(pos, offset)
        except Exception as e:
            # Catch and re-raise with more context
            print(f"[ADBActionExecutor] Error executing '{action_name}' at {pos}: {e}")
            raise
