"""
Base Component Class
All components inherit from this abstract base class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseComponent(ABC):
    """Abstract base class for all TeamAI components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        """
        Initialize component
        
        Args:
            config: Component-specific configuration
            mock_mode: If True, return mock data instead of making real calls
        """
        self.config = config or {}
        self.mock_mode = mock_mode
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute component logic
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate component configuration
        Must be implemented by subclasses
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock_mode={self.mock_mode})"
