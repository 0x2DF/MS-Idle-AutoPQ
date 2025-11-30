# workflow.py
from core.vision import ScreenCapture, ImageMatcher
from core.input import ActionExecutor
from core.utils.debug import DebugManager
from core.constants import MAX_RECOVERY_ATTEMPTS
from ..models import Loop
from .execution_context import ExecutionContext
from .step_executor import StepExecutor
from ..state import StateRecovery, WorkflowFlattener, LoopStateManager
from ..utils import WorkflowPrinter


class WorkflowEngine:
    """Orchestrates workflow execution by coordinating flattening, state management, and printing."""
    
    def __init__(self, steps, capture, matcher, actions, debug,
                 max_recovery_attempts=MAX_RECOVERY_ATTEMPTS,
                 step_executor_factory=None, state_recovery_factory=None):
        """
        Initialize WorkflowEngine with explicit dependencies.
        
        Args:
            steps: List of workflow steps to execute
            capture: ScreenCapture instance
            matcher: ImageMatcher instance
            actions: ActionExecutor instance
            debug: DebugManager instance
            max_recovery_attempts: Maximum number of recovery attempts
            step_executor_factory: Optional factory function for creating StepExecutor
            state_recovery_factory: Optional factory function for creating StateRecovery
        """
        self.steps = steps
        self.max_recovery_attempts = max_recovery_attempts
        
        # Store injected dependencies
        self._capture = capture
        self._matcher = matcher
        self._actions = actions
        self._debug = debug
        
        # Store factories for creating executors
        self._step_executor_factory = step_executor_factory or (lambda ctx: StepExecutor(ctx))
        self._state_recovery_factory = state_recovery_factory or (
            lambda ctx, steps, max_attempts: StateRecovery(ctx, steps, max_attempts)
        )
        
        # Workflow components (initialized in run())
        self.context = None
        self.flattened_steps = []
        self.loop_state_manager = None
        self.printer = None

    def run(self, stop_event=None):
        print(f"[Workflow] Starting with {len(self.steps)} items")
        
        # Initialize execution context
        self.context = ExecutionContext(self._capture, self._matcher, self._actions, self._debug, stop_event)
        
        # Flatten workflow structure
        flattener = WorkflowFlattener()
        self.flattened_steps, loop_states = flattener.flatten(self.steps)
        
        # Initialize workflow components
        self.loop_state_manager = LoopStateManager(loop_states, self.context)
        self.printer = WorkflowPrinter(loop_states)
        
        # Create executors using factories
        step_executor = self._step_executor_factory(self.context)
        state_recovery = self._state_recovery_factory(self.context, self.flattened_steps, self.max_recovery_attempts)
        
        # Execute workflow
        current_index = 0
        while current_index < len(self.flattened_steps):
            if self.context.is_stopped():
                print("[Workflow] Stop requested")
                return
            
            step_info = self.flattened_steps[current_index]
            step = step_info['step']
            loop_id = step_info['loop_id']
            
            # Print step information
            self.printer.print_step_info(step, loop_id, current_index, len(self.flattened_steps))
            
            # Execute step
            success = step_executor.execute(step)
            
            if success:
                # Determine next step
                current_index = self.loop_state_manager.get_next_index(
                    current_index, loop_id, len(self.flattened_steps)
                )
                if current_index is None:
                    return
            else:
                # Attempt recovery
                print(f"  ✗ Step '{step.name}' failed after {step.retries} retries")
                recovered_index = state_recovery.attempt_recovery()
                
                if recovered_index is not None:
                    recovered_step = self.flattened_steps[recovered_index]['step']
                    print(f"  → Recovered to step {recovered_index + 1}: {recovered_step.name}")
                    current_index = recovered_index
                else:
                    print(f"[Workflow] Could not determine current state. Exiting.")
                    return
        
        print("[Workflow] Complete")

