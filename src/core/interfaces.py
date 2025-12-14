"""
Interfaces Module
Defines contracts and protocols for components.

OOP Concepts:
- Interface pattern (pure abstract classes)
- Protocol pattern for duck typing
- Type hints for type safety
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol
from pathlib import Path


class IDataExtractor(ABC):
    """
    Interface for data extraction components.
    
    OOP: Pure interface pattern - all methods are abstract
    """
    
    @abstractmethod
    def extract(self, source: Any) -> List[Dict]:
        """
        Extract data from source.
        
        Args:
            source: Data source
            
        Returns:
            List of extracted data dictionaries
        """
        pass
    
    @abstractmethod
    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get extraction statistics.
        
        Returns:
            Dictionary with stats
        """
        pass


class IOutputFormatter(ABC):
    """
    Interface for output formatting.
    
    OOP: Defines contract for formatters
    """
    
    @abstractmethod
    def format(self, data: Any) -> str:
        """
        Format data for output.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """
        Get formatter name.
        
        Returns:
            Name of format
        """
        pass


class IValidationStrategy(ABC):
    """
    Interface for validation strategies (Strategy Pattern).
    
    OOP: Strategy pattern interface
    """
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate data using this strategy.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        pass
    
    @abstractmethod
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get validation report.
        
        Returns:
            Validation report dictionary
        """
        pass


class Parseable(Protocol):
    """
    Protocol for parseable objects (Duck Typing).
    
    OOP: Protocol pattern - any object with these methods
    can be used as parseable.
    """
    
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """Parse method signature"""
        ...
    
    def validate(self) -> bool:
        """Validate method signature"""
        ...
    
    @property
    def total_items(self) -> int:
        """Total items property"""
        ...


class Writeable(Protocol):
    """
    Protocol for writeable objects.
    
    OOP: Any object implementing these can be written
    """
    
    def write(self, data: Any) -> bool:
        """Write method signature"""
        ...
    
    @property
    def output_path(self) -> str:
        """Output path property"""
        ...


class Validatable(Protocol):
    """
    Protocol for validatable objects.
    
    OOP: Duck typing for validation
    """
    
    def validate(self, data: Any) -> bool:
        """Validate method signature"""
        ...
    
    @property
    def is_valid(self) -> bool:
        """Validation status property"""
        ...


# Type aliases for better code documentation
ParserType = IDataExtractor
WriterType = IOutputFormatter
ValidatorType = IValidationStrategy

# Module exports
__all__ = [
    'IDataExtractor',
    'IOutputFormatter',
    'IValidationStrategy',
    'Parseable',
    'Writeable',
    'Validatable',
    'ParserType',
    'WriterType',
    'ValidatorType'
]