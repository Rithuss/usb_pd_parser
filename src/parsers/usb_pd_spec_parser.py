"""
USB PD Specification Content Parser
Demonstrates INHERITANCE and POLYMORPHISM.

OOP Concepts:
- INHERITANCE: Inherits from BaseParser
- POLYMORPHISM: Different parse() implementation
- ENCAPSULATION: Private content extraction
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from core.base_classes import BaseParser


class USBPDSpecParser(BaseParser):
    """
    Specification content parser for USB PD.
    
    OOP Principles:
    - INHERITANCE: Extends BaseParser
    - POLYMORPHISM: Custom parse() implementation
    - ENCAPSULATION: Private content extraction
    """
    
    def __init__(self, doc_title: str):
        """
        Initialize specification parser.
        
        Args:
            doc_title: Document title
        """
        # INHERITANCE: Call parent constructor
        super().__init__(doc_title)
        
        # ENCAPSULATION: Private attributes
        self.__content_sections = []
        self.__total_content_length = 0
        self.__sections_with_content = 0
        self.__avg_content_length = 0.0
        
        # ENCAPSULATION: Protected attributes
        self._parser_type = "SPEC"
        self._buffer_size = 0
    
    # PROPERTY: Read-only access
    @property
    def content_sections(self) -> List[Dict]:
        """Get content sections"""
        return self.__content_sections.copy()
    
    @property
    def total_content_length(self) -> int:
        """Get total content length in characters"""
        return self.__total_content_length
    
    @property
    def avg_content_length(self) -> float:
        """Get average content length per section"""
        return self.__avg_content_length
    
    # POLYMORPHISM: Override abstract method
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse specification content from text data.
        
        POLYMORPHISM: Content-specific parsing.
        
        Args:
            text_data: Dictionary of page_num -> text
            
        Returns:
            List of content section dictionaries
        """
        sections = []
        current_section = None
        buffer = []
        
        for page_num, content in text_data.items():
            if not content:
                continue
            
            lines = content.split("\n")
            
            for line in lines:
                line_stripped = line.strip()
                
                # Detect new section
                if self.__is_section_header(line_stripped):
                    # Save previous section
                    if current_section and buffer:
                        section_data = self.__create_section_entry(
                            current_section,
                            buffer
                        )
                        sections.append(section_data)
                    
                    # Start new section
                    current_section = self.__extract_section_id(
                        line_stripped
                    )
                    buffer = []
                    
                    # Include section title in content
                    parts = line_stripped.split(maxsplit=1)
                    if len(parts) > 1:
                        buffer.append(parts[1])
                
                else:
                    # ENHANCED: Capture ALL text for better coverage
                    if line_stripped:
                        buffer.append(line_stripped)
                        self._buffer_size += len(line_stripped)
        
        # Don't forget last section
        if current_section and buffer:
            section_data = self.__create_section_entry(
                current_section,
                buffer
            )
            sections.append(section_data)
        
        # Calculate statistics
        self.__calculate_content_stats(sections)
        
        # Store results
        self.__content_sections = sections
        self._mark_as_parsed(sections)
        
        return sections
    
    # POLYMORPHISM: Override abstract method
    def validate(self) -> bool:
        """
        Validate spec parsing results.
        
        Returns:
            True if valid
        """
        if not self.is_parsed:
            return False
        
        if self.total_items == 0:
            return False
        
        # Check content quality
        if self.__sections_with_content < self.total_items * 0.5:
            return False
        
        return True
    
    # ENCAPSULATION: Private helper
    def __is_section_header(self, line: str) -> bool:
        """
        Check if line is a section header.
        
        Args:
            line: Line of text
            
        Returns:
            True if section header
        """
        if not line:
            return False
        
        return line[0].isdigit() if line else False
    
    # ENCAPSULATION: Private helper
    def __extract_section_id(self, line: str) -> str:
        """
        Extract section ID from line.
        
        Args:
            line: Line of text
            
        Returns:
            Section ID
        """
        parts = line.split(maxsplit=1)
        return parts[0].rstrip('.')
    
    # ENCAPSULATION: Private helper
    def __create_section_entry(
        self,
        section_id: str,
        buffer: List[str]
    ) -> Dict:
        """
        Create section entry dictionary.
        
        Args:
            section_id: Section identifier
            buffer: Content lines
            
        Returns:
            Section dictionary
        """
        content_text = " ".join(buffer).strip()
        
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "content": content_text
        }
    
    # ENCAPSULATION: Private statistics
    def __calculate_content_stats(self, sections: List[Dict]):
        """
        Calculate content statistics.
        
        Args:
            sections: List of sections
        """
        self.__total_content_length = sum(
            len(s.get("content", ""))
            for s in sections
        )
        
        self.__sections_with_content = sum(
            1 for s in sections
            if s.get("content", "").strip()
        )
        
        self.__avg_content_length = (
            self.__total_content_length / len(sections)
            if sections else 0.0
        )
    
    # PROTECTED METHOD: Get parsing statistics
    def _get_parse_stats(self) -> Dict:
        """
        Get spec parsing statistics.
        
        Returns:
            Statistics dictionary
        """
        base_stats = self._get_metadata()
        spec_stats = {
            "parser_type": self._parser_type,
            "total_content_length": self.__total_content_length,
            "sections_with_content": self.__sections_with_content,
            "avg_content_length": round(self.__avg_content_length, 2),
            "buffer_size": self._buffer_size
        }
        
        return {**base_stats, **spec_stats}
    
    # SPECIAL METHOD: Iteration
    def __iter__(self):
        """Iterate over content sections"""
        return iter(self.__content_sections)
    
    # SPECIAL METHOD: Item access
    def __getitem__(self, index: int) -> Dict:
        """Get section by index"""
        return self.__content_sections[index]
    
    # SPECIAL METHOD: Contains check
    def __contains__(self, section_id: str) -> bool:
        """Check if section ID exists"""
        return any(
            entry["section_id"] == section_id
            for entry in self.__content_sections
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("spec", USBPDSpecParser)