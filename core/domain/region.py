"""Region value object."""
from typing import Optional, Dict


class Region:
    """Represents a rectangular region (ROI)."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError(f"Region dimensions must be positive: width={width}, height={height}")
        
        self._x = int(x)
        self._y = int(y)
        self._width = int(width)
        self._height = int(height)
    
    @property
    def x(self) -> int:
        return self._x
    
    @property
    def y(self) -> int:
        return self._y
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def right(self) -> int:
        """Right edge x-coordinate."""
        return self._x + self._width
    
    @property
    def bottom(self) -> int:
        """Bottom edge y-coordinate."""
        return self._y + self._height
    
    def to_monitor_dict(self) -> Dict[str, int]:
        """Convert to mss monitor dictionary format."""
        return {
            "left": self._x,
            "top": self._y,
            "width": self._width,
            "height": self._height
        }
    
    def __repr__(self) -> str:
        return f"Region(x={self._x}, y={self._y}, width={self._width}, height={self._height})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Region):
            return False
        return (self._x == other._x and self._y == other._y and 
                self._width == other._width and self._height == other._height)
    
    def __hash__(self) -> int:
        return hash((self._x, self._y, self._width, self._height))
