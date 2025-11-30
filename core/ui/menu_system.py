# menu_system.py
from typing import Optional, Tuple
from .script_browser import ScriptBrowser
from .main_menu import MainMenu
from .execution_mode_menu import ExecutionModeMenu


class MenuSystem:
    """Unified menu system coordinating all menu components."""
    
    def __init__(self, scripts_path="scripts", workflow_loader=None):
        self.script_browser = ScriptBrowser(scripts_path, workflow_loader)
        self.main_menu = MainMenu()
        self.execution_menu = ExecutionModeMenu()
    
    def run(self) -> Optional[Tuple[str, str]]:
        """
        Run the menu system.
        Returns: (script_path, execution_mode) or None if user exits
        """
        while True:
            action = self.main_menu.display()
            
            if action is None:
                return None  # Exit
            
            if action == "scripts":
                script_path = self.script_browser.browse()
                if script_path:
                    execution_mode = self.execution_menu.display()
                    if execution_mode:  # Check if user didn't go back
                        return (script_path, execution_mode)
            
            elif action == "config":
                print("\n[Config] Configuration menu not yet implemented")
                input("Press Enter to continue...")
                continue
