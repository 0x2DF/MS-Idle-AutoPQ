# Core package - Automation framework
# Organized into logical modules for better maintainability

# Re-export commonly used classes for convenience
from .workflow import WorkflowEngine, WorkflowLoader, ExecutionController, Step, Loop
from .vision import ScreenCapture, ImageMatcher
from .input import ActionExecutor
from .ui import MenuSystem
from .utils import DebugManager, ConfigLoader
from .exceptions import (
    WorkflowError,
    WorkflowLoadError,
    WorkflowFileNotFoundError,
    WorkflowSyntaxError,
    WorkflowValidationError,
    StepExecutionError,
    TemplateNotFoundError,
    StateVerificationError,
    StateRecoveryError,
    ConfigurationError,
    WindowNotFoundError,
    ActionError,
    UnknownActionError
)

__all__ = [
    # Workflow
    'WorkflowEngine',
    'WorkflowLoader',
    'ExecutionController',
    'Step',
    'Loop',
    # Vision
    'ScreenCapture',
    'ImageMatcher',
    # Input
    'ActionExecutor',
    # UI
    'MenuSystem',
    # Utils
    'DebugManager',
    'ConfigLoader',
    # Exceptions
    'WorkflowError',
    'WorkflowLoadError',
    'WorkflowFileNotFoundError',
    'WorkflowSyntaxError',
    'WorkflowValidationError',
    'StepExecutionError',
    'TemplateNotFoundError',
    'StateVerificationError',
    'StateRecoveryError',
    'ConfigurationError',
    'WindowNotFoundError',
    'ActionError',
    'UnknownActionError',
]
