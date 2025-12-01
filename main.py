# main.py
import sys
import msvcrt
import threading
from core.workflow import WorkflowEngine, WorkflowLoader, ExecutionController
from core.utils import ConfigLoader, LogLevel, set_log_level, get_logger
from core.utils.debug import DebugManager
from core.utils.window_manager import create_window_manager
from core.vision import ScreenCapture, ImageMatcher, WindowCaptureStrategy, FullScreenCaptureStrategy, ADBScreenCapture
from core.input import ActionExecutor, ADBActionExecutor, ADBClient, Win32ActionExecutor
from core.ui import MenuSystem


def create_capture_strategy(config, debug, logger):
    """Create appropriate capture strategy based on configuration."""
    window_name = config.get("window_name")
    
    if window_name:
        logger.debug(f"Using window capture for: {window_name}")
        window_manager = create_window_manager()
        return WindowCaptureStrategy(window_manager, window_name, debug=debug)
    else:
        logger.debug("Using full screen capture")
        return FullScreenCaptureStrategy()


def create_capture_and_actions(config, debug, logger):
    """
    Create capture and action executor together.
    """
    input_method = config.get("input_method", "pyautogui").lower()
    window_name = config.get("window_name")
    
    if input_method == "adb":
        logger.info("⚙ Using ADB mode (capture + input)")
        device_id = config.get("adb_device_id")
        if device_id:
            logger.debug(f"Target ADB device: {device_id}")
        
        # Create single ADB client for both capture and actions
        adb_client = ADBClient(device_id=device_id)
        
        # Use ADB for both screen capture and input
        capture = ADBScreenCapture(adb_client, debug)
        actions = ADBActionExecutor(device_id=device_id)
        
        logger.debug("Using ADB screencap (coordinates will match perfectly)")
        return capture, actions
    
    elif input_method == "win32":
        logger.info("⚙ Using Win32 mode (window capture + PostMessage)")
        if not window_name:
            raise ValueError("Win32 mode requires window_name in config")
        
        # Use window capture + Win32 input (no cursor movement!)
        capture_strategy = create_capture_strategy(config, debug, logger)
        capture = ScreenCapture(strategy=capture_strategy)
        
        window_manager = create_window_manager()
        actions = Win32ActionExecutor(window_manager, window_name)
        
        logger.debug("Cursor will NOT move (using PostMessage)")
        return capture, actions
    
    else:
        logger.info("⚙ Using PyAutoGUI mode (window capture + mouse control)")
        capture_strategy = create_capture_strategy(config, debug, logger)
        capture = ScreenCapture(strategy=capture_strategy)
        actions = ActionExecutor()
        return capture, actions


def listen_for_stop(controller, logger):
    """Listen for 'q' key press to stop execution."""
    logger.info("Press 'q' to stop execution\n")
    
    while controller.is_running:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'q':
                controller.stop()
                break


def main():
    # Parse command line arguments
    debug_enabled = "-debug" in sys.argv or "--debug" in sys.argv
    verbose_enabled = "-verbose" in sys.argv or "--verbose" in sys.argv
    quiet_enabled = "-quiet" in sys.argv or "--quiet" in sys.argv
    
    # Set log level based on flags
    if quiet_enabled:
        set_log_level(LogLevel.QUIET)
    elif verbose_enabled:
        set_log_level(LogLevel.VERBOSE)
    elif debug_enabled:
        set_log_level(LogLevel.DEBUG)
    else:
        set_log_level(LogLevel.INFO)
    
    logger = get_logger()
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
                logger.info("\n👋 Exiting application")
                break
            
            selected_workflow, execution_mode = result
            
            # Load the selected workflow
            logger.debug(f"Loading workflow: {selected_workflow}")
            steps = loader.load(selected_workflow)
            
            # Check if workflow loaded successfully
            if steps is None:
                logger.error("Failed to load workflow. Please check the YAML file for errors.")
                logger.info("Returning to menu...\n")
                continue
            
            if len(steps) == 0:
                logger.error("Workflow has no steps. Please check the YAML file.")
                logger.info("Returning to menu...\n")
                continue
            
            # Create all dependencies explicitly
            # Note: These must be created fresh for each execution due to thread-local storage
            capture, actions = create_capture_and_actions(config, debug, logger)
            scale_range = config.get("scale_range")
            matcher = ImageMatcher(debug=debug, scale_range=scale_range)
            
            # Wire dependencies into workflow engine
            engine = WorkflowEngine(
                steps=steps,
                capture=capture,
                matcher=matcher,
                actions=actions,
                debug=debug
            )
            controller = ExecutionController(engine)
            
            # Show workflow summary
            workflow_name = selected_workflow.replace('\\', '/').replace('.yaml', '')
            logger.info(f"\n▶ {workflow_name} ({execution_mode})")
            
            # Start execution
            controller.start(mode=execution_mode)
            
            # Listen for stop signal in a separate thread
            listener_thread = threading.Thread(target=listen_for_stop, args=(controller, logger))
            listener_thread.daemon = True
            listener_thread.start()
            
            # Wait for execution to complete
            controller.wait()
            
            logger.info("\n↩ Returning to menu...\n")
    
    except KeyboardInterrupt:
        logger.info("\n\n⚠ Interrupted by user")
    
    finally:
        debug.cleanup()
        logger.debug("Cleanup complete")


if __name__ == "__main__":
    main()
