"""
Spec Validation Strategy
Validates specification content data.

OOP Concepts:
- STRATEGY PATTERN: Interchangeable validation
- INHERITANCE: Inherits from BaseValidator
- POLYMORPHISM: Custom validate() implementation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from core.base_classes import BaseValidator


class SpecValidationStrategy(BaseValidator):
    """
    Validation strategy for specification content.
    
    OOP Principles:
    - STRATEGY PATTERN: Interchangeable validation
    - INHERITANCE: Extends BaseValidator
    - POLYMORPHISM: Custom validate() logic
    """
    
    def __init__(self):
        """Initialize spec content validator"""
        # INHERITANCE: Call parent
        super().__init__("Spec Content Validator")
        
        # ENCAPSULATION: Private attributes
        self.__min_sections = 1000
        self.__min_content_quality = 0.75  # 75% threshold
        self.__empty_sections = []
        self.__short_sections = []
        self.__total_content_length = 0
        
        # ENCAPSULATION: Protected
        self._quality_threshold = self.__min_content_quality
        self._min_content_length = 50  # chars
    
    # PROPERTY: Read-only access
    @property
    def min_content_quality(self) -> float:
        """Minimum content quality threshold"""
        return self.__min_content_quality
    
    @property
    def empty_sections(self) -> List[str]:
        """Get list of empty section IDs"""
        return self.__empty_sections.copy()
    
    @property
    def total_content_length(self) -> int:
        """Get total content length"""
        return self.__total_content_length
    
    # POLYMORPHISM: Override validate method
    def validate(self, data: List[Dict]) -> bool:
        """
        Validate spec content data.
        
        POLYMORPHISM: Content-specific validation.
        
        Args:
            data: List of content entries
            
        Returns:
            True if valid
        """
        # Reset previous validation
        self._reset()
        
        # Rule 1: Check minimum sections
        if not self.__validate_section_count(data):
            return False
        
        # Rule 2: Validate content quality
        if not self.__validate_content_quality(data):
            return False
        
        # Rule 3: Check for required fields
        if not self.__validate_required_fields(data):
            return False
        
        # Rule 4: Validate content coverage
        if not self.__validate_content_coverage(data):
            return False
        
        # Mark as valid if all pass
        if self.error_count == 0:
            self._mark_valid()
            return True
        
        return False
    
    # ENCAPSULATION: Private validation
    def __validate_section_count(self, data: List[Dict]) -> bool:
        """
        Validate section count.
        
        Args:
            data: Content entries
            
        Returns:
            True if valid count
        """
        count = len(data)
        
        if count < self.__min_sections:
            self._add_error(
                f"Insufficient sections: {count} "
                f"(minimum: {self.__min_sections})"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def __validate_content_quality(
        self,
        data: List[Dict]
    ) -> bool:
        """
        Validate content quality.
        
        Args:
            data: Content entries
            
        Returns:
            True if quality meets threshold
        """
        total_sections = len(data)
        sections_with_content = 0
        
        for entry in data:
            content = entry.get("content", "")
            content_length = len(content.strip())
            
            self.__total_content_length += content_length
            
            if content_length == 0:
                self.__empty_sections.append(
                    entry.get("section_id", "unknown")
                )
            elif content_length < self._min_content_length:
                self.__short_sections.append(
                    entry.get("section_id", "unknown")
                )
                sections_with_content += 1
            else:
                sections_with_content += 1
        
        # Calculate quality percentage
        quality = sections_with_content / total_sections
        
        if quality < self.__min_content_quality:
            self._add_error(
                f"Content quality too low: {quality:.1%} "
                f"(threshold: {self.__min_content_quality:.1%})"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def __validate_required_fields(self, data: List[Dict]) -> bool:
        """
        Validate required fields.
        
        Args:
            data: Content entries
            
        Returns:
            True if required fields present
        """
        required_fields = ["section_id", "content", "doc_title"]
        missing_count = 0
        
        for entry in data:
            for field in required_fields:
                if field not in entry:
                    missing_count += 1
        
        if missing_count > 0:
            self._add_error(
                f"Missing required fields in {missing_count} entries"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def __validate_content_coverage(self, data: List[Dict]) -> bool:
        """
        Validate content coverage.
        
        Args:
            data: Content entries
            
        Returns:
            True if coverage is adequate
        """
        # Calculate average content length
        if len(data) > 0:
            avg_length = self.__total_content_length / len(data)
        else:
            avg_length = 0
        
        # Check if average is reasonable
        if avg_length < 100:  # Too short on average
            self._add_error(
                f"Average content too short: {avg_length:.0f} chars"
            )
            return False
        
        # Check empty sections percentage
        empty_pct = len(self.__empty_sections) / len(data)
        if empty_pct > 0.05:  # More than 5% empty
            self._add_error(
                f"Too many empty sections: {empty_pct:.1%}"
            )
            return False
        
        return True
    
    # PROTECTED METHOD: Get validation details
    def _get_validation_details(self) -> Dict:
        """
        Get detailed validation results.
        
        Returns:
            Validation details dictionary
        """
        return {
            "validator_name": self.validator_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": self.validation_errors,
            "total_content_length": self.__total_content_length,
            "empty_sections": len(self.__empty_sections),
            "short_sections": len(self.__short_sections),
            "quality_threshold": self._quality_threshold
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """String representation"""
        status = "Valid" if self.is_valid else "Invalid"
        return (
            f"SpecValidationStrategy({status}, "
            f"content_length={self.__total_content_length})"
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import ValidatorFactory
    ValidatorFactory.register_validator(
        "spec",
        SpecValidationStrategy
    )