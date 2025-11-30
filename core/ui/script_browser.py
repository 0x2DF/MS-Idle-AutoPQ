# script_browser.py
from pathlib import Path
from typing import Optional, Dict, List
import msvcrt


class ScriptBrowser:
    """Hierarchical browser for navigating script directories."""
    
    def __init__(self, scripts_path="scripts", workflow_loader=None):
        self.scripts_path = Path(scripts_path)
        self.workflow_loader = workflow_loader
    
    def browse(self) -> Optional[str]:
        """
        Browse scripts hierarchically and return selected script path.
        Returns None if user cancels.
        """
        current_path = self.scripts_path
        
        while True:
            items = self._get_directory_items(current_path)
            
            if not items:
                print(f"[Browser] No items found in '{current_path.relative_to(self.scripts_path)}'")
                return None
            
            choice = self._display_directory_menu(current_path, items)
            
            if choice is None:
                # Go back or exit
                if current_path == self.scripts_path:
                    return None  # Exit from root
                else:
                    current_path = current_path.parent  # Go back
            elif choice["type"] == "directory":
                current_path = choice["path"]
            else:  # script file
                return str(choice["path"].relative_to(self.scripts_path)).replace("\\", "/")
    
    def _get_directory_items(self, directory: Path) -> List[Dict]:
        """Get directories and scripts in the current directory."""
        items = []
        
        # Get subdirectories
        for item in sorted(directory.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                items.append({
                    "type": "directory",
                    "name": item.name,
                    "path": item
                })
        
        # Get YAML files in current directory
        for item in sorted(directory.glob("*.yaml")):
            # Get display name from workflow if loader is available
            relative_path = str(item.relative_to(self.scripts_path)).replace("\\", "/")
            if self.workflow_loader:
                display_name = self.workflow_loader.get_workflow_name(relative_path)
            else:
                display_name = item.stem
            
            items.append({
                "type": "script",
                "name": display_name,
                "path": item
            })
        
        return items
    
    def _display_directory_menu(self, current_path: Path, items: List[Dict]) -> Optional[Dict]:
        """Display menu for current directory and return selected item."""
        # Calculate relative path for display
        if current_path == self.scripts_path:
            location = "Scripts"
        else:
            location = str(current_path.relative_to(self.scripts_path))
        
        # Add back option to items list
        back_label = "Exit" if current_path == self.scripts_path else "← Back"
        
        selected = 0
        
        while True:
            # Clear and display menu
            print("\033[2J\033[H", end="")  # Clear screen
            print("\n" + "=" * 50)
            print(f"  Location: {location}")
            print("=" * 50)
            
            for idx, item in enumerate(items):
                prefix = "📁" if item["type"] == "directory" else "📄"
                if idx == selected:
                    print(f"> {prefix} {item['name']}")
                else:
                    print(f"  {prefix} {item['name']}")
            
            # Display back option
            if selected == len(items):
                print(f"> {back_label}")
            else:
                print(f"  {back_label}")
            
            print("\nUse ↑/↓ arrows to navigate, Enter to select")
            
            # Get key input
            key = msvcrt.getch()
            
            if key == b'\xe0':  # Arrow key prefix
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    selected = (selected - 1) % (len(items) + 1)
                elif key == b'P':  # Down arrow
                    selected = (selected + 1) % (len(items) + 1)
            elif key == b'\r':  # Enter
                if selected == len(items):
                    return None  # Back or exit
                return items[selected]
            elif key == b'\x1b':  # ESC
                return None
