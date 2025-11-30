# Domain Value Objects

This module contains immutable value objects that represent core domain concepts.

## Value Objects

### Position
Represents a 2D coordinate (x, y).

```python
from core.domain import Position

# Create
pos = Position(100, 200)

# Access
x = pos.x
y = pos.y

# Offset
new_pos = pos.offset(10, 20)  # Returns Position(110, 220)
```

### Region
Represents a rectangular area (x, y, width, height).

```python
from core.domain import Region

# Create
region = Region(10, 20, 100, 50)

# Access
x = region.x
y = region.y
width = region.width
height = region.height
right = region.right  # x + width
bottom = region.bottom  # y + height

# For mss library
monitor_dict = region.to_monitor_dict()  # {"left": 10, "top": 20, "width": 100, "height": 50}
```

### MatchResult
Represents the result of template matching.

```python
from core.domain import MatchResult, NO_MATCH, create_match_result

# Successful match
result = MatchResult(Position(100, 200), confidence=0.95)
if result:  # Truthy
    print(result.position)  # Position(100, 200)
    print(result.confidence)  # 0.95

# Failed match (Null Object pattern)
result = NO_MATCH
if not result:  # Falsy
    print("No match found")

# Factory function
result = create_match_result(position, confidence)  # Returns MatchResult or NO_MATCH
```

## Benefits

1. **Type Safety**: Clear types instead of ambiguous tuples
2. **Immutability**: Value objects cannot be modified after creation
3. **Validation**: Constructor validates inputs (e.g., positive dimensions)
4. **Expressiveness**: `position.x` is clearer than `pos[0]`
5. **No Tuple Confusion**: Forces proper usage throughout codebase

## Usage in YAML

When defining workflows, ROI and offset are still specified as lists in YAML:

```yaml
steps:
  - name: "Click Button"
    find: "assets/button.png"
    action: "click"
    roi: [100, 200, 300, 400]  # [x, y, width, height]
    offset: [10, 5]  # [x, y]
```

The WorkflowLoader automatically converts these to Position and Region objects.
