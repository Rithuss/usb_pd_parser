"""Table of Contents parser for USB PD specification.

Extracts numbered TOC entries from page text and tracks
hierarchy information like levels and parent relationships.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Union
from core.base_classes import BaseParser


class TOCParsingState:
    """Holds current parsing state during TOC extraction.
    
    Tracks current page, collected entries, hierarchy levels,
    and maximum depth found during parsing.
    """
    
    def __init__(self):
        self.current_page = None
        self.entries = []
        self.hierarchy_levels = {}
        self.max_depth = 0


class USBPDTOCParser(BaseParser):
    """Extracts Table of Contents entries from specification text.
    
    Finds lines starting with section numbers, extracts titles and page numbers,
    and calculates hierarchy levels and parent relationships.
    """
    
    def __init__(self, doc_title: str):
        """Set up the TOC parser with document title."""
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
        """Get list of all parsed TOC entries."""
        return self.__toc_entries.copy()
    
    @property
    def max_depth(self) -> int:
        """Get the deepest hierarchy level found."""
        return self.__max_depth
    
    @property
    def hierarchy_levels(self) -> Dict[int, int]:
        """Get count of sections at each hierarchy level."""
        return self.__hierarchy_levels.copy()
    
    # POLYMORPHISM: Override abstract method
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """Extract TOC entries from page text data.
        
        Processes each page, finds TOC lines, and builds hierarchy.
        Returns list of TOC entry dictionaries with metadata.
        """
        self._state = TOCParsingState()
        
        for page_num, content in text_data.items():
            if not content:
                continue
            
            self._process_page_content(content, page_num)
        
        # Store results
        self.__toc_entries = self._state.entries
        self.__hierarchy_levels = self._state.hierarchy_levels
        self.__max_depth = self._state.max_depth
        self._mark_as_parsed(self.__toc_entries)
        
        return self.__toc_entries
    
    def _process_page_content(self, content: str, page_num: int):
        """Process all lines in a page for TOC entries."""
        self._state.current_page = page_num
        for line in content.split("\n"):
            self._process_toc_line(line)
    
    def _process_toc_line(self, line: str):
        """Check if a line contains a TOC entry and add it."""
        entry = self._parse_toc_line(line)
        if entry:
            self._add_toc_entry(entry)
    
    def _add_toc_entry(self, entry: Dict):
        """Add a TOC entry and update hierarchy statistics."""
        self._state.entries.append(entry)
        self._pattern_matched += 1
        self._update_hierarchy(entry["level"])
    
    def _update_hierarchy(self, level: int):
        """Update counts for hierarchy levels."""
        self._state.hierarchy_levels[level] = (
            self._state.hierarchy_levels.get(level, 0) + 1
        )
        self._state.max_depth = max(self._state.max_depth, level)
    
    # POLYMORPHISM: Override abstract method
    def validate(self) -> bool:
        """Check if parsing was successful and hierarchy looks reasonable."""
        if not self.is_parsed:
            return False
        
        if self.total_items == 0:
            return False
        
        # Check for reasonable hierarchy
        if self.__max_depth < 1 or self.__max_depth > 10:
            return False
        
        return True
    
    # ENCAPSULATION: Private helper method
    def _parse_toc_line(self, line: str) -> Union[Dict, None]:
        """Extract TOC entry data from a line, or return None if not a TOC line."""
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
        parent_id = self._calculate_parent_id(section_id)
        
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "title": title,
            "page": self._state.current_page,
            "level": level,
            "parent_id": parent_id,
            "full_path": f"{section_id} {title}"
        }
    
    # ENCAPSULATION: Private helper
    def _calculate_parent_id(self, section_id: str) -> Union[str, None]:
        """Find the parent section ID in the hierarchy."""
        if '.' not in section_id:
            return None
        
        parts = section_id.split('.')
        parent_parts = parts[:-1]
        return '.'.join(parent_parts)
    
    # PROTECTED METHOD: Get parsing statistics
    def _get_parse_stats(self) -> Dict:
        """Get parsing statistics and metadata."""
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
        """Iterate over parsed TOC entries."""
        return iter(self.__toc_entries)
    
    # SPECIAL METHOD: Item access
    def __getitem__(self, index: int) -> Dict:
        """Return the TOC entry at the given index."""
        return self.__toc_entries[index]
    
    # SPECIAL METHOD: Contains check
    def __contains__(self, section_id: str) -> bool:
        """Return True if a section id exists among parsed entries."""
        return any(
            entry["section_id"] == section_id
            for entry in self.__toc_entries
        )


# Register with factory (will do this later)
if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("toc", USBPDTOCParser)