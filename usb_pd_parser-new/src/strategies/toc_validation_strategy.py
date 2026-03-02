"""Table of Contents validation strategy.

Implements checks for TOC entries such as minimum section count,
hierarchy depth, duplicate section ids and presence of required
fields. Intended to be used through the `BaseValidator` interface.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from core.base_classes import BaseValidator


class TOCValidationState:
    """Encapsulates the state during TOC validation operations."""
    
    def __init__(self, data: List[Dict]):
        self.data = data
        self.total_sections = len(data)
        self.validated_sections = []
        self.hierarchy_issues = []
        self.max_level = 0


class TOCValidationStrategy(BaseValidator):
    """Validate TOC entry lists.

    The validator accepts a list of TOC dictionaries and applies a
    set of rules: minimum count, hierarchy checks, id uniqueness and
    required field presence. Results and details are exposed via
    ``_get_validation_details()``.
    """
    
    def __init__(self):
        """Initialize thresholds and internal tracking lists."""
        # INHERITANCE: Call parent
        super().__init__("TOC Validator")
        
        # ENCAPSULATION: Private attributes
        self.__min_sections = 1000
        self.__max_hierarchy_depth = 10
        
        # ENCAPSULATION: Protected
        self._validation_rules = {
            "min_sections": self.__min_sections,
            "max_depth": self.__max_hierarchy_depth
        }
    
    # PROPERTY: Read-only access
    @property
    def min_sections(self) -> int:
        """Return the configured minimum number of TOC sections."""
        return self.__min_sections
    
    @property
    def validated_sections(self) -> List[str]:
        """Return a copy of section ids that passed basic checks."""
        return getattr(self, '_validation_state', TOCValidationState([])).validated_sections.copy()
    
    # POLYMORPHISM: Override validate method
    def validate(self, data: List[Dict]) -> bool:
        """Validate a list of TOC entry dictionaries.

        Returns True if all checks pass; otherwise records errors and
        returns False.
        """
        # Reset previous validation
        self._reset()
        
        # Create validation state
        self._validation_state = TOCValidationState(data)
        
        # Apply all validation rules
        validation_rules = [
            self._validate_section_count,
            self._validate_hierarchy,
            self._validate_section_ids,
            self._validate_required_fields
        ]
        
        all_passed = True
        for rule in validation_rules:
            if not rule():
                all_passed = False
        
        # Mark as valid if all checks pass
        if all_passed and self.error_count == 0:
            self._mark_valid()
            return True
        
        return False
    
    # ENCAPSULATION: Private validation rules
    def _validate_section_count(self) -> bool:
        """Ensure the total number of TOC entries meets the minimum."""
        count = self._validation_state.total_sections
        
        if count < self.__min_sections:
            self._add_error(
                f"Insufficient sections: {count} "
                f"(minimum: {self.__min_sections})"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def _validate_hierarchy(self) -> bool:
        """Check hierarchy depth and basic parent-child consistency."""
        self._analyze_hierarchy()
        
        if not self._validate_hierarchy_depth():
            return False
        
        if not self._validate_hierarchy_consistency():
            return False
        
        return True
    
    def _analyze_hierarchy(self):
        """Analyze hierarchy structure and collect issues."""
        for entry in self._validation_state.data:
            level = entry.get("level", 0)
            self._validation_state.max_level = max(self._validation_state.max_level, level)
            
            # Check parent-child relationship
            if level > 1:
                parent_id = entry.get("parent_id")
                if not parent_id:
                    self._add_hierarchy_issue(entry)
    
    def _add_hierarchy_issue(self, entry: Dict):
        """Add a hierarchy issue to the tracking list."""
        self._validation_state.hierarchy_issues.append(
            entry.get("section_id", "unknown")
        )
    
    def _validate_hierarchy_depth(self) -> bool:
        """Validate that hierarchy depth doesn't exceed maximum."""
        if self._validation_state.max_level > self.__max_hierarchy_depth:
            self._add_error(
                f"Hierarchy too deep: {self._validation_state.max_level} levels "
                f"(max: {self.__max_hierarchy_depth})"
            )
            return False
        return True
    
    def _validate_hierarchy_consistency(self) -> bool:
        """Validate that hierarchy issues are within acceptable limits."""
        issue_threshold = self._validation_state.total_sections * 0.1
        if len(self._validation_state.hierarchy_issues) > issue_threshold:
            self._add_error(
                f"Too many hierarchy issues: "
                f"{len(self._validation_state.hierarchy_issues)}"
            )
            return False
        return True
    
    # ENCAPSULATION: Private validation
    def _validate_section_ids(self) -> bool:
        """Verify section id uniqueness and collect validated ids."""
        seen_ids = set()
        duplicates = []
        
        for entry in self._validation_state.data:
            section_id = entry.get("section_id", "")
            
            if section_id in seen_ids:
                duplicates.append(section_id)
            else:
                seen_ids.add(section_id)
                self._validation_state.validated_sections.append(section_id)
        
        if duplicates:
            self._add_error(
                f"Duplicate section IDs found: {len(duplicates)}"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def _validate_required_fields(self) -> bool:
        """Ensure each entry contains required keys (id, title, page, level, full_path)."""
        required_fields = [
            "section_id",
            "title",
            "page",
            "level",
            "full_path"
        ]
        
        missing_fields_count = self._count_missing_fields(required_fields)
        
        if missing_fields_count > 0:
            self._add_error(
                f"Missing required fields in {missing_fields_count} "
                f"entries"
            )
            return False
        
        return True
    
    def _count_missing_fields(self, required_fields: List[str]) -> int:
        """Count total missing required fields across all entries."""
        missing_count = 0
        
        for entry in self._validation_state.data:
            missing_count += self._count_missing_fields_in_entry(entry, required_fields)
        
        return missing_count
    
    def _count_missing_fields_in_entry(self, entry: Dict, required_fields: List[str]) -> int:
        """Count missing required fields in a single entry."""
        return sum(1 for field in required_fields if field not in entry)
    
    # PROTECTED METHOD: Get validation details
    def _get_validation_details(self) -> Dict:
        """Return a dict summarizing validation status, counts and rules."""
        state = getattr(self, '_validation_state', TOCValidationState([]))
        return {
            "validator_name": self.validator_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": self.validation_errors,
            "validated_sections": len(state.validated_sections),
            "hierarchy_issues": len(state.hierarchy_issues),
            "validation_rules": self._validation_rules
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Return a short string indicating validation status and error count."""
        status = "Valid" if self.is_valid else "Invalid"
        return (
            f"TOCValidationStrategy({status}, "
            f"errors={self.error_count})"
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import ValidatorFactory
    ValidatorFactory.register_validator(
        "toc",
        TOCValidationStrategy
    )