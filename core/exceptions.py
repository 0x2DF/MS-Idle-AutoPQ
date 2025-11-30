# exceptions.py
"""
Custom exceptions for the workflow automation system.

This module defines domain-specific exceptions that provide clear,
actionable error messages and enable proper error handling throughout
the application.

Exception Hierarchy:
    WorkflowError (base)
    ├── WorkflowLoadError
    │   ├── WorkflowFileNotFoundError
    │   ├── WorkflowSyntaxError
    │   └── WorkflowValidationError
    ├── StepExecutionError
    │   ├── TemplateNotFoundError
    │   └── StateVerificationError
    └── StateRecoveryError
"""


class WorkflowError(Exception):
    """Base exception for all workflow-related errors."""
    pass


# Workflow Loading Errors
class WorkflowLoadError(WorkflowError):
    """Base exception for errors during workflow loading."""
    pass


class WorkflowFileNotFoundError(WorkflowLoadError):
    """Raised when a workflow file cannot be found."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Workflow file not found: {file_path}")


class WorkflowSyntaxError(WorkflowLoadError):
    """Raised when a workflow file has invalid YAML syntax."""
    
    def __init__(self, file_path: str, details: str):
        self.file_path = file_path
        self.details = details
        super().__init__(f"Invalid YAML syntax in {file_path}: {details}")


class WorkflowValidationError(WorkflowLoadError):
    """Raised when a workflow file has invalid structure or missing required fields."""
    
    def __init__(self, message: str, file_path: str = None, step_index: int = None):
        self.file_path = file_path
        self.step_index = step_index
        
        error_msg = message
        if file_path:
            error_msg = f"{message} in {file_path}"
        if step_index is not None:
            error_msg = f"{error_msg} (step {step_index})"
        
        super().__init__(error_msg)


# Step Execution Errors
class StepExecutionError(WorkflowError):
    """Base exception for errors during step execution."""
    
    def __init__(self, step_name: str, message: str):
        self.step_name = step_name
        super().__init__(f"Step '{step_name}': {message}")


class TemplateNotFoundError(StepExecutionError):
    """Raised when a template image file cannot be found."""
    
    def __init__(self, step_name: str, template_path: str):
        self.template_path = template_path
        super().__init__(step_name, f"Template not found: {template_path}")


class StateVerificationError(StepExecutionError):
    """Raised when state verification fails after an action."""
    
    def __init__(self, step_name: str, retries: int):
        self.retries = retries
        super().__init__(step_name, f"State verification failed after {retries} attempts")


# State Recovery Errors
class StateRecoveryError(WorkflowError):
    """Raised when state recovery fails or max attempts exceeded."""
    
    def __init__(self, attempts: int, max_attempts: int):
        self.attempts = attempts
        self.max_attempts = max_attempts
        super().__init__(
            f"Could not recover workflow state after {attempts} attempts (max: {max_attempts})"
        )


# Configuration Errors
class ConfigurationError(WorkflowError):
    """Raised when there's an error in configuration or setup."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class WindowNotFoundError(ConfigurationError):
    """Raised when a specified window cannot be found."""
    
    def __init__(self, window_name: str):
        self.window_name = window_name
        super().__init__(f"Window '{window_name}' not found")


# Action Errors
class ActionError(WorkflowError):
    """Raised when an action execution fails."""
    
    def __init__(self, action_name: str, message: str):
        self.action_name = action_name
        super().__init__(f"Action '{action_name}': {message}")


class UnknownActionError(ActionError):
    """Raised when an unknown action is requested."""
    
    def __init__(self, action_name: str):
        super().__init__(action_name, "Unknown action type")
