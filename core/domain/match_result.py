"""Match result value object."""
from typing import Optional
from .position import Position


class MatchResult:
    """Represents the result of a template matching operation."""
    
    def __init__(self, position: Position, confidence: float):
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")
        
        self._position = position
        self._confidence = confidence
    
    @property
    def position(self) -> Position:
        return self._position
    
    @property
    def confidence(self) -> float:
        return self._confidence
    
    @property
    def found(self) -> bool:
        """Convenience property to check if match was successful."""
        return True
    
    def __repr__(self) -> str:
        return f"MatchResult(position={self._position}, confidence={self._confidence:.3f})"
    
    def __bool__(self) -> bool:
        """Allow using MatchResult in boolean context."""
        return True


class NoMatch:
    """Represents a failed match (Null Object pattern)."""
    
    @property
    def position(self) -> None:
        return None
    
    @property
    def confidence(self) -> float:
        return 0.0
    
    @property
    def found(self) -> bool:
        return False
    
    def __repr__(self) -> str:
        return "NoMatch()"
    
    def __bool__(self) -> bool:
        return False


# Singleton instance for no match
NO_MATCH = NoMatch()


def create_match_result(position: Optional[Position], confidence: float) -> MatchResult | NoMatch:
    """Factory function to create appropriate match result."""
    if position is None:
        return NO_MATCH
    return MatchResult(position, confidence)
