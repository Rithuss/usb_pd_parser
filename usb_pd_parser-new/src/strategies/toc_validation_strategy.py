"""
TOC Validation Strategy
Validates Table of Contents data.

OOP Concepts:
- STRATEGY PATTERN: Interchangeable validation algorithm
- INHERITANCE: Inherits from BaseValidator
- POLYMORPHISM: Custom validate() implementation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from core.base_classes import BaseValidator


class TOCValidationStrategy(BaseValidator):
    """
    Validation strategy for TOC data.
    
    OOP Principles:
    - STRATEGY PATTERN: Interchangeable validation
    - INHERITANCE: Extends BaseValidator
    - POLYMORPHISM: Custom validate() logic
    """
    
    def __init__(self):
        """Initialize TOC validator"""
        # INHERITANCE: Call parent
        super().__init__("TOC Validator")
        
        # ENCAPSULATION: Private attributes
        self.__min_sections = 1000
        self.__max_hierarchy_depth = 10
        self.__validated_sections = []
        self.__hierarchy_issues = []
        
        # ENCAPSULATION: Protected
        self._validation_rules = {
            "min_sections": self.__min_sections,
            "max_depth": self.__max_hierarchy_depth
        }
    
    # PROPERTY: Read-only access
    @property
    def min_sections(self) -> int:
        """Minimum expected sections"""
        return self.__min_sections
    
    @property
    def validated_sections(self) -> List[str]:
        """Get validated section IDs"""
        return self.__validated_sections.copy()
    
    # POLYMORPHISM: Override validate method
    def validate(self, data: List[Dict]) -> bool:
        """
        Validate TOC data.
        
        POLYMORPHISM: TOC-specific validation logic.
        
        Args:
            data: List of TOC entries
            
        Returns:
            True if valid
        """
        # Reset previous validation
        self._reset()
        
        # Rule 1: Check minimum sections
        if not self.__validate_section_count(data):
            return False
        
        # Rule 2: Validate hierarchy structure
        if not self.__validate_hierarchy(data):
            return False
        
        # Rule 3: Validate section IDs
        if not self.__validate_section_ids(data):
            return False
        
        # Rule 4: Validate required fields
        if not self.__validate_required_fields(data):
            return False
        
        # Mark as valid if all checks pass
        if self.error_count == 0:
            self._mark_valid()
            return True
        
        return False
    
    # ENCAPSULATION: Private validation rules
    def __validate_section_count(self, data: List[Dict]) -> bool:
        """
        Validate minimum section count.
        
        Args:
            data: TOC entries
            
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
    def __validate_hierarchy(self, data: List[Dict]) -> bool:
        """
        Validate hierarchy structure.
        
        Args:
            data: TOC entries
            
        Returns:
            True if hierarchy is valid
        """
        max_level = 0
        
        for entry in data:
            level = entry.get("level", 0)
            max_level = max(max_level, level)
            
            # Check parent-child relationship
            if level > 1:
                parent_id = entry.get("parent_id")
                if not parent_id:
                    self.__hierarchy_issues.append(
                        entry.get("section_id", "unknown")
                    )
        
        if max_level > self.__max_hierarchy_depth:
            self._add_error(
                f"Hierarchy too deep: {max_level} levels "
                f"(max: {self.__max_hierarchy_depth})"
            )
            return False
        
        if len(self.__hierarchy_issues) > len(data) * 0.1:
            self._add_error(
                f"Too many hierarchy issues: "
                f"{len(self.__hierarchy_issues)}"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def __validate_section_ids(self, data: List[Dict]) -> bool:
        """
        Validate section ID format.
        
        Args:
            data: TOC entries
            
        Returns:
            True if section IDs are valid
        """
        seen_ids = set()
        duplicates = []
        
        for entry in data:
            section_id = entry.get("section_id", "")
            
            # Check for duplicates
            if section_id in seen_ids:
                duplicates.append(section_id)
            else:
                seen_ids.add(section_id)
                self.__validated_sections.append(section_id)
        
        if duplicates:
            self._add_error(
                f"Duplicate section IDs found: {len(duplicates)}"
            )
            return False
        
        return True
    
    # ENCAPSULATION: Private validation
    def __validate_required_fields(self, data: List[Dict]) -> bool:
        """
        Validate required fields in entries.
        
        Args:
            data: TOC entries
            
        Returns:
            True if all required fields present
        """
        required_fields = [
            "section_id",
            "title",
            "page",
            "level",
            "full_path"
        ]
        
        missing_fields_count = 0
        
        for entry in data:
            for field in required_fields:
                if field not in entry:
                    missing_fields_count += 1
        
        if missing_fields_count > 0:
            self._add_error(
                f"Missing required fields in {missing_fields_count} "
                f"entries"
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
            "validated_sections": len(self.__validated_sections),
            "hierarchy_issues": len(self.__hierarchy_issues),
            "validation_rules": self._validation_rules
        }
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """String representation"""
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