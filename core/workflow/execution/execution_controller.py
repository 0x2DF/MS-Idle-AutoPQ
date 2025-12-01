# execution_controller.py
import threading
import time
from core.constants import LOOP_ITERATION_DELAY
from core.utils import get_logger


class ExecutionController:
    """Controls workflow execution with stop and loop capabilities."""
    
    def __init__(self, workflow_engine):
        self.engine = workflow_engine
        self.stop_event = threading.Event()
        self.execution_thread = None
        self.is_running = False
        self.logger = get_logger()
    
    def start(self, mode="once"):
        """
        Start workflow execution in a separate thread.
        mode: "once" or "loop"
        """
        if self.is_running:
            self.logger.info("⚠ Workflow is already running")
            return
        
        self.stop_event.clear()
        self.is_running = True
        
        if mode == "once":
            self.execution_thread = threading.Thread(target=self._run_once)
        else:  # loop
            self.execution_thread = threading.Thread(target=self._run_loop)
        
        self.execution_thread.daemon = True
        self.execution_thread.start()
    
    def stop(self):
        """Signal the workflow to stop."""
        if not self.is_running:
            return
        
        self.logger.info("\n⏹ Stopping workflow...")
        self.stop_event.set()
    
    def wait(self):
        """Wait for the execution thread to complete."""
        if self.execution_thread and self.execution_thread.is_alive():
            self.execution_thread.join()
    
    def _run_once(self):
        """Execute workflow once."""
        try:
            self.engine.run(self.stop_event)
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
        finally:
            self.is_running = False
            self.logger.debug("Execution complete")
    
    def _run_loop(self):
        """Execute workflow in a loop until stopped."""
        iteration = 1
        try:
            while not self.stop_event.is_set():
                self.logger.info(f"\n🔄 Starting iteration {iteration}")
                
                if hasattr(self.engine, 'context') and self.engine.context:
                    self.engine.context.recovery_attempts = 0
                
                self.engine.run(self.stop_event)
                
                if self.stop_event.is_set():
                    break
                
                self.logger.info(f"✓ Iteration {iteration} complete")
                iteration += 1
                
                time.sleep(LOOP_ITERATION_DELAY)
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
        finally:
            self.is_running = False
            self.logger.info("■ Loop execution stopped")
