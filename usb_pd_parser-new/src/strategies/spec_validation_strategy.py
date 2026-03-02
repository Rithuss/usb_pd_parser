"""Specification content validation strategy.

Validates that parsed specification sections have good content quality,
required fields, and meet minimum standards. Uses ValidationState to
track metrics during validation.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from core.base_classes import BaseValidator


class ValidationState:
    """Holds data and metrics during specification content validation.
    
    Tracks section counts, content quality metrics, and identifies
    empty or short sections for validation reporting.
    """
    
    def __init__(self, data: List[Dict]):
        self.data = data
        self.total_sections = len(data)
        self.sections_with_content = 0
        self.total_content_length = 0
        self.empty_sections = []
        self.short_sections = []


class SpecValidationStrategy(BaseValidator):
    """Validates specification content entries for quality and completeness.
    
    Checks that sections have sufficient content, required fields are present,
    and content quality meets minimum standards. Uses ValidationState to track
    metrics and validation results.
    """
    
    def __init__(self):
        """Set up validation thresholds and initialize the validator."""
        # INHERITANCE: Call parent
        super().__init__("Spec Content Validator")
        
        # ENCAPSULATION: Private attributes
        self.__min_sections = 1000
        self.__min_content_quality = 0.75  # 75% threshold
        
        # ENCAPSULATION: Protected
        self._quality_threshold = self.__min_content_quality
        self._min_content_length = 50  # chars
    
    # PROPERTY: Read-only access
    @property
    def min_content_quality(self) -> float:
        """Get the minimum required quality percentage for content."""
        return self.__min_content_quality
    
    @property
    def empty_sections(self) -> List[str]:
        """Get list of section IDs that have no content."""
        return getattr(self, '_validation_state', ValidationState([])).empty_sections.copy()
    
    @property
    def total_content_length(self) -> int:
        """Get total character count across all sections."""
        return getattr(self, '_validation_state', ValidationState([])).total_content_length
    
    # POLYMORPHISM: Override validate method
    def validate(self, data: List[Dict]) -> bool:
        """Check if specification content meets quality standards.
        
        Runs all validation rules and returns True if all pass.
        Records any errors found during validation.
        """
        # Reset previous validation
        self._reset()
        
        # Create validation state
        self._validation_state = ValidationState(data)
        
        # Apply all validation rules
        validation_rules = [
            self._validate_section_count,
            self._validate_content_quality,
            self._validate_required_fields,
            self._validate_content_coverage
        ]
        
        all_passed = True
        for rule in validation_rules:
            if not rule():
                all_passed = False
        
        # Mark as valid if all pass
        if all_passed and self.error_count == 0:
            self._mark_valid()
            return True
        
        return False
    
    # ENCAPSULATION: Private validation
    def _validate_section_count(self) -> bool:
        """Check if there are enough sections to be valid."""
        count = self._validation_state.total_sections
        
        if count < self.__min_sections:
            self._add_error(
                f"Insufficient sections: {count} "
                f"(minimum: {self.__min_sections})"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def _validate_content_quality(self) -> bool:
        """Check if enough sections have meaningful content."""
        self._analyze_content_entries()
        
        # Calculate quality percentage
        quality = self._validation_state.sections_with_content / self._validation_state.total_sections
        
        if quality < self.__min_content_quality:
            self._add_error(
                f"Content quality too low: {quality:.1%} "
                f"(threshold: {self.__min_content_quality:.1%})"
            )
            return False
        
        return True
    
    def _analyze_content_entries(self):
        """Examine each section and categorize by content length."""
        for entry in self._validation_state.data:
            content = entry.get("content", "")
            content_length = len(content.strip())
            
            self._validation_state.total_content_length += content_length
            
            if content_length == 0:
                self._add_empty_section(entry)
            elif content_length < self._min_content_length:
                self._add_short_section(entry)
                self._validation_state.sections_with_content += 1
            else:
                self._validation_state.sections_with_content += 1
    
    def _add_empty_section(self, entry: Dict):
        """Record a section that has no content."""
        self._validation_state.empty_sections.append(
            entry.get("section_id", "unknown")
        )
    
    def _add_short_section(self, entry: Dict):
        """Record a section that has very little content."""
        self._validation_state.short_sections.append(
            entry.get("section_id", "unknown")
        )
    
    # ENCAPSULATION: Private validation
    def _validate_required_fields(self) -> bool:
        """Check that all sections have required data fields."""
        required_fields = ["section_id", "content", "doc_title"]
        missing_count = self._count_missing_fields(required_fields)
        
        if missing_count > 0:
            self._add_error(
                f"Missing required fields in {missing_count} entries"
            )
            return False
        
        return True
    
    def _count_missing_fields(self, required_fields: List[str]) -> int:
        """Count how many required fields are missing across all sections."""
        missing_count = 0
        
        for entry in self._validation_state.data:
            missing_count += self._count_missing_fields_in_entry(entry, required_fields)
        
        return missing_count
    
    def _count_missing_fields_in_entry(self, entry: Dict, required_fields: List[str]) -> int:
        """Count missing required fields in one section."""
        return sum(1 for field in required_fields if field not in entry)
    
    # ENCAPSULATION: Private validation
    def _validate_content_coverage(self) -> bool:
        """Check overall content quality metrics."""
        if not self._validate_average_content_length():
            return False
        
        if not self._validate_empty_sections_percentage():
            return False
        
        return True
    
    def _validate_average_content_length(self) -> bool:
        """Check if sections have enough content on average."""
        avg_length = self._calculate_average_content_length()
        
        if avg_length < 100:  # Too short on average
            self._add_error(
                f"Average content too short: {avg_length:.0f} chars"
            )
            return False
        
        return True
    
    def _validate_empty_sections_percentage(self) -> bool:
        """Check if too many sections are empty."""
        empty_pct = len(self._validation_state.empty_sections) / self._validation_state.total_sections
        
        if empty_pct > 0.05:  # More than 5% empty
            self._add_error(
                f"Too many empty sections: {empty_pct:.1%}"
            )
            return False
        
        return True
    
    def _calculate_average_content_length(self) -> float:
        """Calculate average characters per section."""
        if self._validation_state.total_sections > 0:
            return self._validation_state.total_content_length / self._validation_state.total_sections
        return 0
    
    # PROTECTED METHOD: Get validation details
    def _get_validation_details(self) -> Dict:
        """Get summary of validation results and metrics."""
        state = getattr(self, '_validation_state', ValidationState([]))
        return {
            "validator_name": self.validator_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": self.validation_errors,
            "total_content_length": state.total_content_length,
            "empty_sections": len(state.empty_sections),
            "short_sections": len(state.short_sections),
            "quality_threshold": self._quality_threshold
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Get a short description of the validator's current state."""
        status = "Valid" if self.is_valid else "Invalid"
        content_length = getattr(self, '_validation_state', ValidationState([])).total_content_length
        return (
            f"SpecValidationStrategy({status}, "
            f"content_length={content_length})"
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import ValidatorFactory
    ValidatorFactory.register_validator(
        "spec",
        SpecValidationStrategy
    )