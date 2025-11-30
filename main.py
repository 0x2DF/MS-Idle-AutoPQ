# main.py
import sys
import msvcrt
import threading
from core.workflow import WorkflowEngine, WorkflowLoader, ExecutionController
from core.utils import ConfigLoader
from core.utils.debug import DebugManager
from core.utils.window_manager import create_window_manager
from core.vision import ScreenCapture, ImageMatcher, WindowCaptureStrategy, FullScreenCaptureStrategy
from core.input import ActionExecutor
from core.ui import MenuSystem


def create_capture_strategy(config, debug):
    """Create appropriate capture strategy based on configuration."""
    window_name = config.get("window_name")
    
    if window_name:
        print(f"[Config] Using window capture for: {window_name}")
        window_manager = create_window_manager()
        return WindowCaptureStrategy(window_manager, window_name, debug=debug)
    else:
        print("[Config] Using full screen capture")
        return FullScreenCaptureStrategy()


def listen_for_stop(controller):
    """Listen for 'q' key press to stop execution."""
    print("[Press 'q' to stop execution]\n")
    
    while controller.is_running:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'q':
                controller.stop()
                break


def main():
    # Check for debug flag and create debug manager
    debug_enabled = "-debug" in sys.argv or "--debug" in sys.argv
    debug = DebugManager(enabled=debug_enabled)
    
    # Load configuration
    config_loader = ConfigLoader("config.yaml")
    config = config_loader.load()
    
    # Initialize workflow loader and menu system
    loader = WorkflowLoader(base_path="scripts")
    menu_system = MenuSystem(scripts_path="scripts", workflow_loader=loader)
    
    # Main menu loop
    try:
        while True:
            # Display menu and get user selection
            result = menu_system.run()
            
            if result is None:
                print("\n[Main] Exiting application")
                break
            
            selected_workflow, execution_mode = result
            
            # Load the selected workflow
            print(f"\n[Main] Loading workflow: {selected_workflow}")
            steps = loader.load(selected_workflow)
            
            # Check if workflow loaded successfully
            if steps is None:
                print("[Main] Failed to load workflow. Please check the YAML file for errors.")
                print("[Main] Returning to menu...\n")
                continue
            
            if len(steps) == 0:
                print("[Main] Workflow has no steps. Please check the YAML file.")
                print("[Main] Returning to menu...\n")
                continue
            
            # Create all dependencies explicitly
            # Note: These must be created fresh for each execution due to thread-local storage
            capture_strategy = create_capture_strategy(config, debug)
            capture = ScreenCapture(strategy=capture_strategy)
            matcher = ImageMatcher(debug=debug)
            actions = ActionExecutor()
            
            # Wire dependencies into workflow engine
            engine = WorkflowEngine(
                steps=steps,
                capture=capture,
                matcher=matcher,
                actions=actions,
                debug=debug
            )
            controller = ExecutionController(engine)
            
            # Start execution
            print(f"[Main] Starting workflow in '{execution_mode}' mode")
            controller.start(mode=execution_mode)
            
            # Listen for stop signal in a separate thread
            listener_thread = threading.Thread(target=listen_for_stop, args=(controller,))
            listener_thread.daemon = True
            listener_thread.start()
            
            # Wait for execution to complete
            controller.wait()
            
            print("\n[Main] Returning to menu...\n")
    
    except KeyboardInterrupt:
        print("\n\n[Main] Interrupted by user")
    
    finally:
        debug.cleanup()
        print("[Main] Cleanup complete")


if __name__ == "__main__":
    main()
