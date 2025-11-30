# coordinate_transformer.py
from typing import Optional
from core.domain import Position, Region


class CoordinateTransformer:
    """Handles coordinate transformations between different coordinate spaces."""
    
    def __init__(self, capture):
        """
        Initialize CoordinateTransformer.
        
        Args:
            capture: ScreenCapture instance for getting window offset
        """
        self.capture = capture
    
    def to_global_position(self, relative_pos: Position, roi: Optional[Region] = None) -> Position:
        """
        Convert relative position to global screen coordinates.
        
        Args:
            relative_pos: Position relative to the captured region
            roi: Optional Region of Interest that was used for capture
            
        Returns:
            Position in global screen coordinates
        """
        x, y = relative_pos.x, relative_pos.y
        
        # Add ROI offset if present
        if roi is not None:
            x += roi.x
            y += roi.y
        
        # Add capture offset (window position)
        capture_offset = self.capture.strategy.get_offset()
        x += capture_offset.x
        y += capture_offset.y
        
        return Position(x, y)
    
    def apply_offset(self, position: Position, offset: Position) -> Position:
        """
        Apply an offset to a position.
        
        Args:
            position: Base position
            offset: Offset to apply
            
        Returns:
            New position with offset applied
        """
        return position.offset(offset.x, offset.y)
