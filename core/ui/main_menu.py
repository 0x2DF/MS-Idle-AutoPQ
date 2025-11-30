# main_menu.py
from typing import Optional
import msvcrt
import sys


class MainMenu:
    """Main application menu."""
    
    def display(self) -> Optional[str]:
        """
        Display main menu and return action.
        Returns: 'scripts', 'config', or None (exit)
        """
        options = [
            ("Scripts", "scripts"),
            ("Config (not implemented)", "config"),
            ("Exit", None)
        ]
        
        selected = 0
        
        while True:
            # Clear and display menu
            print("\033[2J\033[H", end="")  # Clear screen
            print("\n" + "=" * 50)
            print("  Workflow Automation - Main Menu")
            print("=" * 50)
            
            for idx, (label, _) in enumerate(options):
                if idx == selected:
                    print(f"> {label}")
                else:
                    print(f"  {label}")
            
            print("\nUse ↑/↓ arrows to navigate, Enter to select")
            
            # Get key input
            key = msvcrt.getch()
            
            if key == b'\xe0':  # Arrow key prefix
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    selected = (selected - 1) % len(options)
                elif key == b'P':  # Down arrow
                    selected = (selected + 1) % len(options)
            elif key == b'\r':  # Enter
                return options[selected][1]
            elif key == b'\x1b':  # ESC
                return None
