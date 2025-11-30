# execution_mode_menu.py
import msvcrt
from typing import Optional


class ExecutionModeMenu:
    """Menu for selecting execution mode."""
    
    @staticmethod
    def display() -> Optional[str]:
        """Display execution mode menu and return user choice."""
        options = [
            ("Run once", "once"),
            ("Loop continuously", "loop"),
            ("← Back", None)
        ]
        
        selected = 0
        
        while True:
            # Clear and display menu
            print("\033[2J\033[H", end="")  # Clear screen
            print("\n" + "=" * 50)
            print("  Execution Mode")
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
