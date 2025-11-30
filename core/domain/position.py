"""Position value object."""


class Position:
    """Represents a 2D coordinate position."""
    
    def __init__(self, x: int, y: int):
        self._x = int(x)
        self._y = int(y)
    
    @property
    def x(self) -> int:
        return self._x
    
    @property
    def y(self) -> int:
        return self._y
    
    def offset(self, dx: int, dy: int) -> 'Position':
        """Return a new Position offset by dx, dy."""
        return Position(self._x + dx, self._y + dy)
    
    def __repr__(self) -> str:
        return f"Position(x={self._x}, y={self._y})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self._x == other._x and self._y == other._y
    
    def __hash__(self) -> int:
        return hash((self._x, self._y))
