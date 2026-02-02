"""
Base Classes Module
Defines abstract base classes demonstrating OOP principles.

OOP Concepts Demonstrated:
- ABSTRACTION: ABC metaclass
- ENCAPSULATION: Private/protected attributes
- INHERITANCE: Base classes for extension
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseParser(ABC):
    """
    Abstract base class for all parsers.
    
    OOP Principles:
    - ABSTRACTION: Defines interface without implementation
    - ENCAPSULATION: Private attributes for internal state
    """
    
    def __init__(self, doc_title: str):
        """
        Initialize parser with document title.
        
        Args:
            doc_title: Title of the document being parsed
        """
        # ENCAPSULATION: Private attributes (double underscore)
        self.__doc_title = doc_title
        self.__parsed_data = []
        self.__metadata = {}
        self.__parse_timestamp = None
        
        # ENCAPSULATION: Protected attributes (single underscore)
        self._total_items = 0
        self._is_parsed = False
    
    # PROPERTY DECORATOR: Controlled access to private data
    @property
    def doc_title(self) -> str:
        """Get document title (read-only)"""
        return self.__doc_title
    
    @property
    def parsed_data(self) -> List[Dict]:
        """Get parsed data (read-only)"""
        return self.__parsed_data.copy()
    
    @property
    def total_items(self) -> int:
        """Get total parsed items"""
        return self._total_items
    
    @property
    def is_parsed(self) -> bool:
        """Check if parsing is complete"""
        return self._is_parsed
    
    # ABSTRACTION: Abstract method - must be implemented by subclasses
    @abstractmethod
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse text data (POLYMORPHISM - different implementations).
        
        Args:
            text_data: Dictionary mapping page numbers to text
            
        Returns:
            List of parsed entries
        """
        pass
    
    # ABSTRACTION: Abstract method for validation
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate parsed data.
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    # PROTECTED METHOD: Internal helper (can be used by subclasses)
    def _mark_as_parsed(self, data: List[Dict]):
        """
        Mark parsing as complete (ENCAPSULATION).
        
        Args:
            data: Parsed data to store
        """
        self.__parsed_data = data
        self._total_items = len(data)
        self._is_parsed = True
        self.__parse_timestamp = datetime.now()
    
    # PROTECTED METHOD: Get metadata
    def _get_metadata(self) -> Dict:
        """Get parser metadata"""
        return {
            "doc_title": self.__doc_title,
            "total_items": self._total_items,
            "is_parsed": self._is_parsed,
            "parsed_at": (
                self.__parse_timestamp.isoformat()
                if self.__parse_timestamp else None
            )
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable string representation"""
        return (
            f"{self.__class__.__name__}("
            f"doc='{self.__doc_title[:30]}...', "
            f"items={self._total_items})"
        )
    
    # SPECIAL METHOD: Developer representation
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"{self.__class__.__name__}("
            f"doc_title='{self.__doc_title}', "
            f"total_items={self._total_items}, "
            f"is_parsed={self._is_parsed})"
        )
    
    # SPECIAL METHOD: Length support
    def __len__(self) -> int:
        """Return number of parsed items"""
        return self._total_items
    
    # SPECIAL METHOD: Equality comparison
    def __eq__(self, other) -> bool:
        """Check equality based on doc_title and data"""
        if not isinstance(other, BaseParser):
            return False
        return (
            self.__doc_title == other.__doc_title and
            self._total_items == other._total_items
        )
    
    # SPECIAL METHOD: Hash support
    def __hash__(self) -> int:
        """Make object hashable"""
        return hash((self.__doc_title, self._total_items))


class BaseOutputWriter(ABC):
    """
    Abstract base class for output writers.
    
    OOP Principles:
    - ABSTRACTION: Defines writer interface
    - ENCAPSULATION: Private file handling
    """
    
    def __init__(self, output_path: str):
        """
        Initialize writer with output path.
        
        Args:
            output_path: Path where output will be written
        """
        # ENCAPSULATION: Private attributes
        self.__output_path = output_path
        self.__write_count = 0
        self.__is_written = False
        
        # ENCAPSULATION: Protected attributes
        self._encoding = "utf-8"
        self._ensure_ascii = False
    
    # PROPERTY: Controlled access
    @property
    def output_path(self) -> str:
        """Get output path (read-only)"""
        return self.__output_path
    
    @property
    def write_count(self) -> int:
        """Get number of items written"""
        return self.__write_count
    
    @property
    def is_written(self) -> bool:
        """Check if write is complete"""
        return self.__is_written
    
    # ABSTRACTION: Abstract write method
    @abstractmethod
    def write(self, data: Any) -> bool:
        """
        Write data to output (POLYMORPHISM).
        
        Args:
            data: Data to write
            
        Returns:
            True if successful
        """
        pass
    
    # PROTECTED METHOD: Mark write as complete
    def _mark_as_written(self, count: int):
        """
        Mark write operation as complete.
        
        Args:
            count: Number of items written
        """
        self.__write_count = count
        self.__is_written = True
    
    # PROTECTED METHOD: Get write statistics
    def _get_write_stats(self) -> Dict:
        """Get write statistics"""
        return {
            "output_path": self.__output_path,
            "write_count": self.__write_count,
            "is_written": self.__is_written,
            "encoding": self._encoding
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable representation"""
        return (
            f"{self.__class__.__name__}("
            f"path='{self.__output_path}', "
            f"written={self.__write_count})"
        )
    
    # SPECIAL METHOD: Developer representation
    def __repr__(self) -> str:
        """Developer representation"""
        return (
            f"{self.__class__.__name__}("
            f"output_path='{self.__output_path}', "
            f"write_count={self.__write_count})"
        )
    
    # SPECIAL METHOD: Boolean conversion
    def __bool__(self) -> bool:
        """Return True if write was successful"""
        return self.__is_written
    
    # SPECIAL METHOD: Length
    def __len__(self) -> int:
        """Return number of items written"""
        return self.__write_count


class BaseValidator(ABC):
    """
    Abstract base class for validators (Strategy Pattern).
    
    OOP Principles:
    - ABSTRACTION: Defines validation interface
    - STRATEGY PATTERN: Interchangeable validation algorithms
    """
    
    def __init__(self, validator_name: str):
        """
        Initialize validator.
        
        Args:
            validator_name: Name of this validator
        """
        # ENCAPSULATION: Private attributes
        self.__validator_name = validator_name
        self.__validation_errors = []
        self.__is_valid = None
        
        # ENCAPSULATION: Protected attributes
        self._error_count = 0
    
    # PROPERTY: Controlled access
    @property
    def validator_name(self) -> str:
        """Get validator name"""
        return self.__validator_name
    
    @property
    def validation_errors(self) -> List[str]:
        """Get validation errors (read-only copy)"""
        return self.__validation_errors.copy()
    
    @property
    def is_valid(self) -> Optional[bool]:
        """Get validation result"""
        return self.__is_valid
    
    @property
    def error_count(self) -> int:
        """Get number of errors"""
        return self._error_count
    
    # ABSTRACTION: Abstract validation method
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate data (POLYMORPHISM).
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        pass
    
    # PROTECTED METHOD: Add validation error
    def _add_error(self, error_message: str):
        """
        Add validation error.
        
        Args:
            error_message: Error description
        """
        self.__validation_errors.append(error_message)
        self._error_count += 1
        self.__is_valid = False
    
    # PROTECTED METHOD: Mark as valid
    def _mark_valid(self):
        """Mark validation as passed"""
        self.__is_valid = True
    
    # PROTECTED METHOD: Reset validation state
    def _reset(self):
        """Reset validation state"""
        self.__validation_errors = []
        self._error_count = 0
        self.__is_valid = None
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable representation"""
        status = (
            "Valid" if self.__is_valid
            else "Invalid" if self.__is_valid is False
            else "Not validated"
        )
        return (
            f"{self.__validator_name}: {status} "
            f"({self._error_count} errors)"
        )
    
    # SPECIAL METHOD: Developer representation
    def __repr__(self) -> str:
        """Developer representation"""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.__validator_name}', "
            f"errors={self._error_count})"
        )
    
    # SPECIAL METHOD: Boolean conversion
    def __bool__(self) -> bool:
        """Return validation result"""
        return self.__is_valid if self.__is_valid is not None else False
    
    # SPECIAL METHOD: Length (number of errors)
    def __len__(self) -> int:
        """Return number of validation errors"""
        return self._error_count
    
    # SPECIAL METHOD: Iteration support
    def __iter__(self):
        """Iterate over validation errors"""
        return iter(self.__validation_errors)


# Module-level constants
__all__ = [
    'BaseParser',
    'BaseOutputWriter',
    'BaseValidator'
]