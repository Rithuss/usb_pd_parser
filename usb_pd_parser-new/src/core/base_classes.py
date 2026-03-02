"""Core abstract base classes used across the project.

Defines lightweight base classes for parsers, writers and
validators. These classes provide small, well-documented helper
methods and properties for common behaviors used by concrete
implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseParser(ABC):
    """Abstract base for parsers that extract structured entries.

    Subclasses implement ``parse(text_data)`` and ``validate()``.
    This base stores parsed items, a document title and provides
    helper methods to mark parsing complete and expose metadata.
    """
    
    def __init__(self, doc_title: str):
        """Store the provided document title and initialize state."""
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
        """Return the document title supplied at construction."""
        return self.__doc_title
    
    @property
    def parsed_data(self) -> List[Dict]:
        """Return a shallow copy of the parsed entries list."""
        return self.__parsed_data.copy()
    
    @property
    def total_items(self) -> int:
        """Number of parsed entries currently stored."""
        return self._total_items
    
    @property
    def is_parsed(self) -> bool:
        """True when `parse()` has been called and results stored."""
        return self._is_parsed
    
    # ABSTRACTION: Abstract method - must be implemented by subclasses
    @abstractmethod
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """Extract structured entries from a page->text mapping.

        Must be implemented by subclasses.
        """
        pass
    
    # ABSTRACTION: Abstract method for validation
    @abstractmethod
    def validate(self) -> bool:
        """Return True when parsed data meets validator-specific checks."""
        pass
    
    # PROTECTED METHOD: Internal helper (can be used by subclasses)
    def _mark_as_parsed(self, data: List[Dict]):
        """Store parsed `data` and update internal counters and timestamp."""
        self.__parsed_data = data
        self._total_items = len(data)
        self._is_parsed = True
        self.__parse_timestamp = datetime.now()
    
    # PROTECTED METHOD: Get metadata
    def _get_metadata(self) -> Dict:
        """Return a small metadata dict about the parser state."""
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
        """Human-readable summary showing class, doc snippet and item count."""
        return (
            f"{self.__class__.__name__}("
            f"doc='{self.__doc_title[:30]}...', "
            f"items={self._total_items})"
        )
    
    # SPECIAL METHOD: Developer representation
    def __repr__(self) -> str:
        """Developer representation including full title and counts."""
        return (
            f"{self.__class__.__name__}("
            f"doc_title='{self.__doc_title}', "
            f"total_items={self._total_items}, "
            f"is_parsed={self._is_parsed})"
        )
    
    # SPECIAL METHOD: Length support
    def __len__(self) -> int:
        """Return the number of parsed items (len semantics)."""
        return self._total_items
    
    # SPECIAL METHOD: Equality comparison
    def __eq__(self, other) -> bool:
        """Equality compares document title and parsed item count."""
        if not isinstance(other, BaseParser):
            return False
        return (
            self.__doc_title == other.__doc_title and
            self._total_items == other._total_items
        )
    
    # SPECIAL METHOD: Hash support
    def __hash__(self) -> int:
        """Provide a stable hash based on title and item count."""
        return hash((self.__doc_title, self._total_items))


class BaseOutputWriter(ABC):
    """Abstract base for output writers.

    Subclasses implement ``write(data)``. This base stores the
    output path and provides helpers to mark writes and expose
    write statistics.
    """
    
    def __init__(self, output_path: str):
        """Store the output file path and initialize writer state."""
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
        """Return the configured output file path."""
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
        """Write `data` to the output target. Implemented by subclasses."""
        pass
    
    # PROTECTED METHOD: Mark write as complete
    def _mark_as_written(self, count: int):
        """Record that `count` items have been written and flip state."""
        self.__write_count = count
        self.__is_written = True
    
    # PROTECTED METHOD: Get write statistics
    def _get_write_stats(self) -> Dict:
        """Return a dict with current write statistics."""
        return {
            "output_path": self.__output_path,
            "write_count": self.__write_count,
            "is_written": self.__is_written,
            "encoding": self._encoding
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Short description showing path and write count."""
        return (
            f"{self.__class__.__name__}("
            f"path='{self.__output_path}', "
            f"written={self.__write_count})"
        )
    
    # SPECIAL METHOD: Developer representation
    def __repr__(self) -> str:
        """Developer representation with constructor-like format."""
        return (
            f"{self.__class__.__name__}("
            f"output_path='{self.__output_path}', "
            f"write_count={self.__write_count})"
        )
    
    # SPECIAL METHOD: Boolean conversion
    def __bool__(self) -> bool:
        """Boolean truthiness indicates whether a write occurred."""
        return self.__is_written
    
    # SPECIAL METHOD: Length
    def __len__(self) -> int:
        """Return the number of items written (len semantics)."""
        return self.__write_count


class BaseValidator(ABC):
    """Abstract base for validation strategies.

    Provides a simple API to record errors, mark valid/invalid and
    expose validation details. Subclasses implement ``validate()``.
    """
    
    def __init__(self, validator_name: str):
        """Store a readable validator name and initialize error state."""
        # ENCAPSULATION: Private attributes
        self.__validator_name = validator_name
        self.__validation_errors = []
        self.__is_valid = None
        
        # ENCAPSULATION: Protected attributes
        self._error_count = 0
    
    # PROPERTY: Controlled access
    @property
    def validator_name(self) -> str:
        """Return the human-readable name of this validator."""
        return self.__validator_name
    
    @property
    def validation_errors(self) -> List[str]:
        """Return a copy of collected validation error messages."""
        return self.__validation_errors.copy()
    
    @property
    def is_valid(self) -> Optional[bool]:
        """Return True/False when validated, or None if not run."""
        return self.__is_valid
    
    @property
    def error_count(self) -> int:
        """Return the number of recorded validation errors."""
        return self._error_count
    
    # ABSTRACTION: Abstract validation method
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate `data`. Must be implemented by subclasses."""
        pass
    
    # PROTECTED METHOD: Add validation error
    def _add_error(self, error_message: str):
        """Record an error message and increment the error counter."""
        self.__validation_errors.append(error_message)
        self._error_count += 1
        self.__is_valid = False
    
    # PROTECTED METHOD: Mark as valid
    def _mark_valid(self):
        """Mark the validator as having passed validation."""
        self.__is_valid = True
    
    # PROTECTED METHOD: Reset validation state
    def _reset(self):
        """Reset error list, counters and valid state to initial."""
        self.__validation_errors = []
        self._error_count = 0
        self.__is_valid = None
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Return a concise status string including error count."""
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
        """Developer-friendly repr showing name and error count."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.__validator_name}', "
            f"errors={self._error_count})"
        )
    
    # SPECIAL METHOD: Boolean conversion
    def __bool__(self) -> bool:
        """Boolean truthiness reflects validation outcome (False if not run)."""
        return self.__is_valid if self.__is_valid is not None else False
    
    # SPECIAL METHOD: Length (number of errors)
    def __len__(self) -> int:
        """Return the number of recorded validation errors."""
        return self._error_count
    
    # SPECIAL METHOD: Iteration support
    def __iter__(self):
        """Iterate over recorded validation error messages."""
        return iter(self.__validation_errors)


# Module-level constants
__all__ = [
    'BaseParser',
    'BaseOutputWriter',
    'BaseValidator'
]