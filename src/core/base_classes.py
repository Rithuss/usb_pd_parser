"""
Core Base Classes
Defines abstract base classes for parsers, writers, and validators.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseParser(ABC):
    """
    Abstract base class for all parsers.
    Demonstrates abstraction, encapsulation, and polymorphism.
    """

    def __init__(self, doc_title: str) -> None:
        self.__doc_title = doc_title
        self._parsed = False
        self._results: List[Dict] = []

    @abstractmethod
    def parse(self, data: Any) -> List[Dict]:
        """Parse input data and return structured output."""
        raise NotImplementedError

    def _mark_as_parsed(self, results: List[Dict]) -> None:
        self._results = results
        self._parsed = True

    @property
    def doc_title(self) -> str:
        return self.__doc_title

    @property
    def is_parsed(self) -> bool:
        return self._parsed

    @property
    def total_items(self) -> int:
        return len(self._results)

    def __len__(self) -> int:
        return self.total_items

    def __iter__(self):
        return iter(self._results)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(items={self.total_items})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseParser):
            return False
        return self._results == other._results


class BaseOutputWriter(ABC):
    """
    Abstract base class for output writers.
    """

    def __init__(self, output_path: str) -> None:
        self.__output_path = output_path
        self._lines_written = 0

    @abstractmethod
    def write(self, data: Any) -> bool:
        """Write data to output."""
        raise NotImplementedError

    @property
    def output_path(self) -> str:
        return self.__output_path

    @property
    def lines_written(self) -> int:
        return self._lines_written

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(path={self.__output_path})"
        )


class BaseValidator(ABC):
    """
    Abstract base class for validators.
    Implements Strategy pattern foundation.
    """

    def __init__(self, name: str) -> None:
        self.__name = name
        self._errors: List[str] = []
        self._is_valid = False

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate data."""
        raise NotImplementedError

    def _add_error(self, message: str) -> None:
        self._errors.append(message)

    def _reset(self) -> None:
        self._errors.clear()
        self._is_valid = False

    def _mark_valid(self) -> None:
        self._is_valid = True

    @property
    def validator_name(self) -> str:
        return self.__name

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def error_count(self) -> int:
        return len(self._errors)

    @property
    def validation_errors(self) -> List[str]:
        return self._errors.copy()

    def __str__(self) -> str:
        status = "VALID" if self._is_valid else "INVALID"
        return f"{self.__class__.__name__}({status})"
