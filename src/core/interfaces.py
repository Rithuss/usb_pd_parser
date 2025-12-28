"""
Interfaces Module
Defines abstract interfaces and protocols for components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Protocol


# -------------------------
# ABSTRACT INTERFACES
# -------------------------

class IDataExtractor(ABC):
    """Interface for data extraction components."""

    @abstractmethod
    def extract(self, source: Any) -> List[Dict]:
        """Extract structured data from source."""
        raise NotImplementedError

    @abstractmethod
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Return extraction statistics."""
        raise NotImplementedError


class IOutputFormatter(ABC):
    """Interface for output formatting components."""

    @abstractmethod
    def format(self, data: Any) -> str:
        """Format data into output string."""
        raise NotImplementedError

    @abstractmethod
    def get_format_name(self) -> str:
        """Return formatter name."""
        raise NotImplementedError


class IValidationStrategy(ABC):
    """Interface for validation strategies."""

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data."""
        raise NotImplementedError

    @abstractmethod
    def get_validation_report(self) -> Dict[str, Any]:
        """Return validation report."""
        raise NotImplementedError


# -------------------------
# PROTOCOLS (DUCK TYPING)
# -------------------------

class Parseable(Protocol):
    """Protocol for parseable objects."""

    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        ...

    @property
    def total_items(self) -> int:
        ...


class Writeable(Protocol):
    """Protocol for writeable objects."""

    def write(self, data: Any) -> bool:
        ...

    @property
    def output_path(self) -> str:
        ...


class Validatable(Protocol):
    """Protocol for validatable objects."""

    def validate(self, data: Any) -> bool:
        ...

    @property
    def is_valid(self) -> bool:
        ...


# -------------------------
# TYPE ALIASES (PEP8)
# -------------------------

parser_type = IDataExtractor
writer_type = IOutputFormatter
validator_type = IValidationStrategy


__all__ = [
    "IDataExtractor",
    "IOutputFormatter",
    "IValidationStrategy",
    "Parseable",
    "Writeable",
    "Validatable",
    "parser_type",
    "writer_type",
    "validator_type",
]
