# workflow_loader.py
import yaml
from pathlib import Path
from core.domain import Region, Position
from core.constants import (
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_END_DELAY,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRIES,
    DEFAULT_START_DELAY,
    DEFAULT_VERIFY_DELAY,
    DEFAULT_VERIFY_RETRIES,
    DEFAULT_BREAK_THRESHOLD,
    DEFAULT_ITERATION_DELAY
)
from core.exceptions import (
    WorkflowFileNotFoundError,
    WorkflowSyntaxError,
    WorkflowValidationError
)
from ..models import Step, Loop
from .step_builder import StepBuilder


class WorkflowLoader:
    """Loads workflow YAML files with support for includes and references."""
    
    def __init__(self, base_path="scripts"):
        self.base_path = Path(base_path)
        self._loaded_cache = {}
    
    def load(self, path):
        """
        Load a workflow file and return list of Step objects.
        Supports 'include' directive to reference other workflow files.
        
        Args:
            path: Path to workflow file
            
        Returns:
            List of Step/Loop objects, or None if loading fails
            
        Note: Returns None for backward compatibility. Consider using
        load_strict() for new code which raises exceptions instead.
        """
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        try:
            return self._load_file(file_path)
        except Exception as e:
            print(f"[WorkflowLoader] Error loading workflow '{path}': {e}")
            return None
    
    def load_strict(self, path):
        """
        Load a workflow file and return list of Step objects.
        Raises exceptions on errors instead of returning None.
        
        Args:
            path: Path to workflow file
            
        Returns:
            List of Step/Loop objects
            
        Raises:
            WorkflowFileNotFoundError: If file doesn't exist
            WorkflowSyntaxError: If YAML is invalid
            WorkflowValidationError: If workflow structure is invalid
        """
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        return self._load_file(file_path)
    
    def get_workflow_name(self, path):
        """
        Get the display name for a workflow.
        Returns the 'name' property from YAML if present, otherwise the filename.
        """
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
            return data.get("name", file_path.stem)
        except Exception:
            return file_path.stem
    
    def _load_file(self, file_path):
        """Internal method to load a file with caching."""
        file_path = Path(file_path).resolve()
        
        # Check cache to avoid reloading
        cache_key = str(file_path)
        if cache_key in self._loaded_cache:
            return self._loaded_cache[cache_key]
        
        # Check if file exists
        if not file_path.exists():
            raise WorkflowFileNotFoundError(str(file_path))
        
        # Load and parse YAML
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowSyntaxError(file_path.name, str(e))
        
        if data is None:
            raise WorkflowValidationError("Empty workflow file", file_path.name)
        
        if not isinstance(data, dict):
            raise WorkflowValidationError(
                f"Workflow file must contain a dictionary, got {type(data).__name__}",
                file_path.name
            )
        
        steps = []
        
        # Process steps, handling includes and loops
        for idx, item in enumerate(data.get("steps", []), 1):
            try:
                if isinstance(item, dict):
                    if "include" in item:
                        # Include another workflow file
                        include_path = item["include"]
                        included_steps = self._resolve_include(include_path, file_path.parent)
                        if included_steps:
                            steps.extend(included_steps)
                    elif "loop" in item:
                        # Loop block - validate it's not None
                        if item["loop"] is None:
                            raise WorkflowValidationError(
                                "Loop definition is empty (check YAML indentation)",
                                file_path.name,
                                idx
                            )
                        loop = self._create_loop(item["loop"], file_path.name, idx)
                        if loop:
                            steps.append(loop)
                    else:
                        # Regular step definition
                        step = self._create_step(item, file_path.name, idx)
                        if step:
                            steps.append(step)
                else:
                    raise WorkflowValidationError(
                        f"Step must be a dictionary, got {type(item).__name__}",
                        file_path.name,
                        idx
                    )
            except WorkflowValidationError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Wrap other exceptions
                raise WorkflowValidationError(str(e), file_path.name, idx)
        
        self._loaded_cache[cache_key] = steps
        return steps
    
    def _resolve_include(self, include_path, current_dir):
        """Resolve and load an included workflow file."""
        include_file = Path(include_path)
        
        # If relative path, resolve relative to current file's directory
        if not include_file.is_absolute():
            include_file = current_dir / include_file
        
        return self._load_file(include_file)
    
    def _create_loop(self, loop_data, filename="", step_num=0):
        """Create a Loop object from YAML data."""
        if not isinstance(loop_data, dict):
            raise WorkflowValidationError(
                f"Loop must be a dictionary, got {type(loop_data).__name__}",
                filename,
                step_num
            )
        
        iterations = loop_data.get("iterations", 1)
        
        # Process nested steps within the loop
        nested_steps = []
        for step_item in loop_data.get("steps", []):
            if isinstance(step_item, dict):
                if "include" in step_item:
                    # Include another workflow file
                    include_path = step_item["include"]
                    included_steps = self._resolve_include(include_path, self.base_path)
                    nested_steps.extend(included_steps)
                elif "loop" in step_item:
                    # Nested loop
                    nested_steps.append(self._create_loop(step_item["loop"]))
                else:
                    # Regular step
                    nested_steps.append(self._create_step(step_item))
            else:
                nested_steps.append(self._create_step(step_item))
        
        return Loop(
            iterations=iterations,
            steps=nested_steps,
            break_on_find=loop_data.get("break_on_find"),
            break_threshold=loop_data.get("break_threshold", DEFAULT_BREAK_THRESHOLD),
            iteration_delay=loop_data.get("iteration_delay", DEFAULT_ITERATION_DELAY)
        )
    
    def _create_step(self, step_data, filename="", step_num=0):
        """
        Create a Step object from YAML data using StepBuilder.
        
        Note: Direct Step() constructor is still available for backward compatibility
        but is considered internal use. Use StepBuilder for new code.
        """
        return StepBuilder.create_from_dict(step_data)
