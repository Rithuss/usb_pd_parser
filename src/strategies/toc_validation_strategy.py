"""
TOC Validation Strategy
Validates Table of Contents data.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from core.base_classes import BaseValidator


class TOCValidationStrategy(BaseValidator):
    
    def __init__(self):
        super().__init__("TOC Validator")
        
        self.__min_sections = 1000
        self.__max_hierarchy_depth = 200
        self.__validated_sections = []
        self.__hierarchy_issues = []
        
        self._validation_rules = {
            "min_sections": self.__min_sections,
            "max_depth": self.__max_hierarchy_depth
        }
    
    @property
    def min_sections(self) -> int:
        return self.__min_sections
    
    @property
    def validated_sections(self) -> List[str]:
        return self.__validated_sections.copy()
    
    def validate(self, data: List[Dict]) -> bool:
        self._reset()
    
        if not self.__validate_section_count(data):
            return False
        
        if not self.__validate_hierarchy(data):
            print(f"DEBUG: Hierarchy failed - errors: {self.validation_errors}")
            return False
    
        if not self.__validate_section_ids(data):
            print(f"DEBUG: Section IDs failed")
            return False
        
        if not self.__validate_required_fields(data):
            print(f"DEBUG: Required fields failed")
            return False
        
        if self.error_count == 0:
            self._mark_valid()
            return True
    
        print(f"DEBUG: Total errors: {self.error_count}")
        return False
    
    
    def __validate_section_count(self, data: List[Dict]) -> bool:
        count = len(data)
        
        if count < self.__min_sections:
            self._add_error(
                f"Insufficient sections: {count} "
                f"(minimum: {self.__min_sections})"
            )
            return False
        
        return True
    
    def __validate_hierarchy(self, data: List[Dict]) -> bool:
        max_level = 0
        
        for entry in data:
            level = entry.get("level", 0)
            max_level = max(max_level, level)
            
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
    
    def __validate_section_ids(self, data: List[Dict]) -> bool:
        seen_ids = set()
        
        for entry in data:
            section_id = entry.get("section_id", "")
            
            if section_id not in seen_ids:
                seen_ids.add(section_id)
                self.__validated_sections.append(section_id)
        
        return True
            
    
    def __validate_required_fields(self, data: List[Dict]) -> bool:
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
    
    def _get_validation_details(self) -> Dict:
        return {
            "validator_name": self.validator_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": self.validation_errors,
            "validated_sections": len(self.__validated_sections),
            "hierarchy_issues": len(self.__hierarchy_issues),
            "validation_rules": self._validation_rules
        }
    
    def __str__(self) -> str:
        status = "Valid" if self.is_valid else "Invalid"
        return (
            f"TOCValidationStrategy({status}, "
            f"errors={self.error_count})"
        )


if __name__ != "__main__":
    from core.factories import ValidatorFactory
    ValidatorFactory.register_validator(
        "toc",
        TOCValidationStrategy
    )