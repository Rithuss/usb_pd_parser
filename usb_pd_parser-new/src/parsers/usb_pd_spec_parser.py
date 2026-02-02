"""
USB PD Specification Content Parser 
"""
import sys
import os
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from typing import Dict, List
from core.base_classes import BaseParser


class SectionDetector:
    """Detects and extracts section information."""
    
    @staticmethod
    def is_section_header(line: str) -> bool:
        """Check if line is a section header."""
        if not line:
            return False
        return line[0].isdigit() if line else False
    
    @staticmethod
    def extract_section_id(line: str) -> str:
        """Extract section ID from line."""
        parts = line.split(maxsplit=1)
        return parts[0].rstrip('.')
    
    @staticmethod
    def extract_section_title(line: str) -> str:
        """Extract section title from line."""
        parts = line.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""


class ContentBuffer:
    """Manages content buffer operations."""
    
    def __init__(self):
        self.buffer = []
        self.size = 0
    
    def add(self, text: str):
        """Add text to buffer."""
        self.buffer.append(text)
        self.size += len(text)
    
    def get_content(self) -> str:
        """Get buffer content as string."""
        return " ".join(self.buffer).strip()
    
    def clear(self):
        """Clear buffer."""
        self.buffer = []
        self.size = 0
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0


class ContentStatistics:
    """Calculates content statistics."""
    
    def __init__(self):
        self.total_length = 0
        self.sections_with_content = 0
        self.avg_length = 0.0
    
    def calculate(self, sections: List[Dict]):
        """Calculate statistics from sections."""
        self.total_length = sum(
            len(s.get("content", "")) for s in sections
        )
        
        self.sections_with_content = sum(
            1 for s in sections if s.get("content", "").strip()
        )
        
        if sections:
            self.avg_length = self.total_length / len(sections)
        else:
            self.avg_length = 0.0


class USBPDSpecParser(BaseParser):
    """Specification content parser with reduced complexity."""
    
    def __init__(self, doc_title: str):
        super().__init__(doc_title)
        
        self.__content_sections = []
        self.__stats = ContentStatistics()
        self._parser_type = "SPEC"
        self._detector = SectionDetector()
    
    @property
    def content_sections(self) -> List[Dict]:
        return self.__content_sections.copy()
    
    @property
    def total_content_length(self) -> int:
        return self.__stats.total_length
    
    @property
    def avg_content_length(self) -> float:
        return self.__stats.avg_length
    
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """Parse specification content from text data.
        
        Ensures all sections are created with required fields:
        doc_title, section_id, title, page, level, parent_id, content.
        """
        sections = []
        current_section = None
        current_title = None
        current_page = None
        buffer = ContentBuffer()
        
        for page_num, content in text_data.items():
            if not content:
                continue
            
            sections, current_section, current_title, current_page, buffer = (
                self._process_page_content(
                    content,
                    sections,
                    current_section,
                    current_title,
                    current_page,
                    page_num,
                    buffer
                )
            )
        
        # Save final section with all required fields
        self._save_section(
            sections,
            current_section,
            current_title,
            current_page,
            buffer
        )
        
        self.__stats.calculate(sections)
        self.__content_sections = sections
        self._mark_as_parsed(sections)
        
        return sections
    
    def _process_page_content(
        self,
        content: str,
        sections: List[Dict],
        current_section: str,
        current_title: str,
        current_page: int,
        page_num: int,
        buffer: ContentBuffer
    ) -> tuple:
        """Process content from a single page."""
        lines = content.split("\n")
        
        for line in lines:
            current_section, current_title, current_page, buffer = (
                self._handle_content_line(
                    line.strip(),
                    sections,
                    current_section,
                    current_title,
                    current_page,
                    page_num,
                    buffer
                )
            )
        
        return sections, current_section, current_title, current_page, buffer
    
    def _handle_content_line(
        self,
        line_stripped: str,
        sections: List[Dict],
        current_section: str,
        current_title: str,
        current_page: int,
        page_num: int,
        buffer: ContentBuffer
    ) -> tuple:
        """Handle a single content line."""
        if self._detector.is_section_header(line_stripped):
            # Save current section before starting new one
            self._save_section(
                sections,
                current_section,
                current_title,
                current_page,
                buffer
            )
            # Start new section and track its page
            current_section, current_title = self._start_new_section(line_stripped)
            current_page = page_num
            return current_section, current_title, current_page, buffer
        else:
            if line_stripped:
                buffer.add(line_stripped)
            return current_section, current_title, current_page, buffer
    
    def _start_new_section(self, line: str) -> tuple:
        """Start a new section and extract metadata."""
        section_id = self._detector.extract_section_id(line)
        title = self._detector.extract_section_title(line)
        
        return section_id, title
    
    def _calculate_section_level(self, section_id: str) -> int:
        """Calculate section hierarchy level from section_id."""
        if not section_id:
            return 0
        return section_id.count('.') + 1
    
    def _get_parent_id(self, section_id: str) -> str:
        """Extract parent section ID from section_id."""
        if not section_id or '.' not in section_id:
            return None
        return '.'.join(section_id.split('.')[:-1])
    
    def _save_section(
        self,
        sections: List[Dict],
        section_id: str,
        title: str,
        page_num: int,
        buffer: ContentBuffer
    ):
        """Save section with all required fields.
        
        Creates valid section records with:
        - doc_title: document title
        - section_id: section identifier
        - title: section title
        - page: page number where section appears
        - level: hierarchy level (calculated from section_id)
        - parent_id: parent section identifier or None
        - content: section content
        
        Does not drop sections when content is present.
        """
        if section_id:
            content_text = buffer.get_content()
            
            # Create section record with all required fields
            section_record = {
                "doc_title": self.doc_title,
                "section_id": section_id,
                "title": title if title else "",
                "page": page_num if page_num else 0,
                "level": self._calculate_section_level(section_id),
                "parent_id": self._get_parent_id(section_id),
                "content": content_text
            }
            
            # Save section even if content is empty (section header was found)
            sections.append(section_record)
            buffer.clear()
    
    def validate(self) -> bool:
        """Validate spec parsing results."""
        return True
    
    def _get_parse_stats(self) -> Dict:
        """Get spec parsing statistics."""
        base_stats = self._get_metadata()
        
        spec_stats = {
            "parser_type": self._parser_type,
            "total_content_length": self.__stats.total_length,
            "sections_with_content": (
                self.__stats.sections_with_content
            ),
            "avg_content_length": round(self.__stats.avg_length, 2)
        }       
        return {**base_stats, **spec_stats}
    
    def __iter__(self):
        return iter(self.__content_sections)
    
    def __getitem__(self, index: int) -> Dict:
        return self.__content_sections[index]
    
    def __contains__(self, section_id: str) -> bool:
        return any(
            entry["section_id"] == section_id
            for entry in self.__content_sections
        )


if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("spec", USBPDSpecParser)