# Workflow Module

Organized workflow execution system for automating game interactions.

## Structure

```
workflow/
├── models/          # Core data structures
│   ├── step.py      # Individual workflow step
│   └── loop.py      # Loop construct for repeating steps
│
├── execution/       # Workflow execution logic
│   ├── workflow.py           # Main WorkflowEngine orchestrator
│   ├── step_executor.py      # Step execution with retry logic
│   ├── execution_context.py  # Shared execution state and resources
│   └── execution_controller.py # Thread-based execution control
│
├── state/           # State management
│   ├── loop_state.py      # Loop iteration tracking
│   ├── state_recovery.py  # Recovery from failed states
│   └── flattener.py       # Flatten nested workflow structures
│
└── utils/           # Utilities and helpers
    ├── step_builder.py          # Fluent builder for creating steps
    ├── workflow_loader.py       # YAML workflow file loader
    ├── coordinate_transformer.py # Coordinate space transformations
    └── printer.py               # Workflow output formatting
```

## Usage

```python
from core.workflow import WorkflowEngine, WorkflowLoader, ExecutionController

# Load workflow from YAML
loader = WorkflowLoader()
steps = loader.load("scripts/my_workflow.yaml")

# Create and run workflow
engine = WorkflowEngine(steps, capture, matcher, actions, debug)
controller = ExecutionController(engine)
controller.start(mode="once")  # or "loop"
```
