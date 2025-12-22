"""
TOC Validation Strategy
Validates Table of Contents data.
"""

from typing import List, Dict
from core.base_classes import BaseValidator


class TOCValidationStrategy(BaseValidator):
    """
    Strategy for validating TOC structure and content.
    """

    _MIN_SECTIONS = 1000
    _MAX_DEPTH = 200

    def __init__(self):
        super().__init__("TOC Validator")

    # --------------------
    # Public API
    # --------------------
    def validate(self, data: List[Dict]) -> bool:
        """
        Validate TOC data using simple, independent rules.
        """
        self._reset()

        if not self._check_section_count(data):
            return False

        if not self._check_hierarchy(data):
            return False

        if not self._check_required_fields(data):
            return False

        self._mark_valid()
        return True

    # --------------------
    # Validation Rules
    # --------------------
    def _check_section_count(self, data: List[Dict]) -> bool:
        if len(data) < self._MIN_SECTIONS:
            self._add_error(
                f"TOC has fewer than {self._MIN_SECTIONS} sections"
            )
            return False
        return True

    def _check_hierarchy(self, data: List[Dict]) -> bool:
        max_level = 0
        missing_parents = 0

        for entry in data:
            level = entry.get("level", 0)
            max_level = max(max_level, level)

            if level > 1 and not entry.get("parent_id"):
                missing_parents += 1

        if max_level > self._MAX_DEPTH:
            self._add_error(
                f"Hierarchy depth exceeds {self._MAX_DEPTH}"
            )
            return False

        if missing_parents > len(data) * 0.1:
            self._add_error(
                "Too many sections missing parent references"
            )
            return False

        return True

    def _check_required_fields(self, data: List[Dict]) -> bool:
        required_fields = {
            "section_id",
            "title",
            "page",
            "level",
            "full_path",
        }

        self.__checked_entries = 0

        for entry in data:
            self.__checked_entries += 1

            if not required_fields.issubset(entry.keys()):
                self._add_error(
                    "One or more TOC entries missing required fields"
                )
                return False

        return True


    # --------------------
    # Helpers
    # --------------------
    def __str__(self) -> str:
        status = "Valid" if self.is_valid else "Invalid"
        return f"TOCValidationStrategy({status})"
