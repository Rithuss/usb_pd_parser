"""
USB PD Table of Contents Parser
Demonstrates INHERITANCE and POLYMORPHISM.

OOP Concepts:
- INHERITANCE: Inherits from BaseParser
- POLYMORPHISM: Overrides parse() and validate()
- ENCAPSULATION: Private methods for internal logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from core.base_classes import BaseParser


class USBPDTOCParser(BaseParser):
    """
    Table of Contents parser for USB PD specification.
    
    OOP Principles:
    - INHERITANCE: Extends BaseParser
    - POLYMORPHISM: Custom implementation of parse()
    - ENCAPSULATION: Private extraction methods
    """
    
    def __init__(self, doc_title: str):
        """
        Initialize TOC parser.
        
        Args:
            doc_title: Document title
        """
        # INHERITANCE: Call parent constructor
        super().__init__(doc_title)
        
        # ENCAPSULATION: Private attributes specific to TOC
        self.__toc_entries = []
        self.__hierarchy_levels = {}
        self.__max_depth = 0
        
        # ENCAPSULATION: Protected attributes
        self._parser_type = "TOC"
        self._pattern_matched = 0
    
    # PROPERTY: Read-only access
    @property
    def toc_entries(self) -> List[Dict]:
        """Get TOC entries (read-only)"""
        return self.__toc_entries.copy()
    
    @property
    def max_depth(self) -> int:
        """Get maximum hierarchy depth"""
        return self.__max_depth
    
    @property
    def hierarchy_levels(self) -> Dict[int, int]:
        """Get sections per hierarchy level"""
        return self.__hierarchy_levels.copy()
    
    # POLYMORPHISM: Override abstract method
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse Table of Contents from text data.
        
        POLYMORPHISM: TOC-specific parsing implementation.
        
        Args:
            text_data: Dictionary of page_num -> text
            
        Returns:
            List of TOC entry dictionaries
        """
        entries = []
        
        for page_num, content in text_data.items():
            if not content:
                continue
            
            # Parse each line for TOC entries
            for line in content.split("\n"):
                entry = self.__parse_toc_line(line, page_num)
                if entry:
                    entries.append(entry)
                    self._pattern_matched += 1
                    
                    # Track hierarchy
                    level = entry["level"]
                    self.__hierarchy_levels[level] = (
                        self.__hierarchy_levels.get(level, 0) + 1
                    )
                    self.__max_depth = max(self.__max_depth, level)
        
        # Store results
        self.__toc_entries = entries
        self._mark_as_parsed(entries)
        
        return entries
    
    # POLYMORPHISM: Override abstract method
    def validate(self) -> bool:
        """
        Validate TOC parsing results.
        
        Returns:
            True if valid
        """
        if not self.is_parsed:
            return False
        
        if self.total_items == 0:
            return False
        
        # Check for reasonable hierarchy
        if self.__max_depth < 1 or self.__max_depth > 10:
            return False
        
        return True
    
    # ENCAPSULATION: Private helper method
    def __parse_toc_line(
        self,
        line: str,
        page_num: int
    ) -> Dict or None:
        """
        Parse a single TOC line (ENCAPSULATION).
        
        Args:
            line: Line of text
            page_num: Current page number
            
        Returns:
            TOC entry dict or None
        """
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            return None
        
        # Check if line starts with a number (section ID)
        if not (line_stripped and line_stripped[0].isdigit()):
            return None
        
        # Extract section ID and title
        parts = line_stripped.split(maxsplit=1)
        section_id = parts[0].rstrip('.')
        title = parts[1] if len(parts) > 1 else ""
        
        # Calculate hierarchy level
        level = section_id.count('.') + 1
        
        # Calculate parent ID
        parent_id = self.__calculate_parent_id(section_id)
        
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "title": title,
            "page": page_num,
            "level": level,
            "parent_id": parent_id,
            "full_path": f"{section_id} {title}"
        }
    
    # ENCAPSULATION: Private helper
    def __calculate_parent_id(self, section_id: str) -> str or None:
        """
        Calculate parent section ID (ENCAPSULATION).
        
        Args:
            section_id: Section identifier
            
        Returns:
            Parent section ID or None
        """
        if '.' not in section_id:
            return None
        
        parts = section_id.split('.')
        parent_parts = parts[:-1]
        return '.'.join(parent_parts)
    
    # PROTECTED METHOD: Get parsing statistics
    def _get_parse_stats(self) -> Dict:
        """
        Get TOC parsing statistics.
        
        Returns:
            Statistics dictionary
        """
        base_stats = self._get_metadata()
        toc_stats = {
            "parser_type": self._parser_type,
            "pattern_matched": self._pattern_matched,
            "max_depth": self.__max_depth,
            "hierarchy_levels": self.__hierarchy_levels
        }
        
        return {**base_stats, **toc_stats}
    
    # SPECIAL METHOD: Iteration support
    def __iter__(self):
        """Iterate over TOC entries"""
        return iter(self.__toc_entries)
    
    # SPECIAL METHOD: Item access
    def __getitem__(self, index: int) -> Dict:
        """Get TOC entry by index"""
        return self.__toc_entries[index]
    
    # SPECIAL METHOD: Contains check
    def __contains__(self, section_id: str) -> bool:
        """Check if section ID exists in TOC"""
        return any(
            entry["section_id"] == section_id
            for entry in self.__toc_entries
        )


# Register with factory (will do this later)
if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("toc", USBPDTOCParser)