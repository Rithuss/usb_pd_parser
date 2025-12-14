"""
USB PD Specification Content Parser - REFACTORED
Fixed: parse() from 68 lines to 18 lines, complexity from 11 to 3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from core.base_classes import BaseParser


class USBPDSpecParser(BaseParser):
    
    def __init__(self, doc_title: str):
        super().__init__(doc_title)
        
        self.__content_sections = []
        self.__total_content_length = 0
        self.__sections_with_content = 0
        self.__avg_content_length = 0.0
        
        self._parser_type = "SPEC"
        self._buffer_size = 0
    
    @property
    def content_sections(self) -> List[Dict]:
        return self.__content_sections.copy()
    
    @property
    def total_content_length(self) -> int:
        return self.__total_content_length
    
    @property
    def avg_content_length(self) -> float:
        return self.__avg_content_length
    
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        sections = []
        current_section = None
        buffer = []
        
        for page_num, content in text_data.items():
            if content:
                current_section, buffer = self._process_page(
                    content, sections, current_section, buffer
                )
        
        self._save_last_section(sections, current_section, buffer)
        self.__calculate_content_stats(sections)
        self.__content_sections = sections
        self._mark_as_parsed(sections)
        
        return sections
    
    def _process_page(self, content: str, sections: list, 
                      current_section: str, buffer: list) -> tuple:
        lines = content.split("\n")
        
        for line in lines:
            line_stripped = line.strip()
            
            if self.__is_section_header(line_stripped):
                current_section, buffer = self._handle_new_section(
                    sections, current_section, buffer, line_stripped
                )
            elif line_stripped:
                buffer.append(line_stripped)
                self._buffer_size += len(line_stripped)
        
        return current_section, buffer
    
    def _handle_new_section(self, sections: list, current_section: str,
                            buffer: list, line: str) -> tuple:
        if current_section and buffer:
            sections.append(self.__create_section_entry(current_section, buffer))
        
        current_section = self.__extract_section_id(line)
        buffer = []
        
        parts = line.split(maxsplit=1)
        if len(parts) > 1:
            buffer.append(parts[1])
        
        return current_section, buffer
    
    def _save_last_section(self, sections: list, current_section: str, buffer: list):
        if current_section and buffer:
            sections.append(self.__create_section_entry(current_section, buffer))
    
    def validate(self) -> bool:
        if not self.is_parsed:
            return False
        
        if self.total_items == 0:
            return False
        
        if self.__sections_with_content < self.total_items * 0.5:
            return False
        
        return True
    
    def __is_section_header(self, line: str) -> bool:
        if not line:
            return False
        
        return line[0].isdigit() if line else False
    
    def __extract_section_id(self, line: str) -> str:
        parts = line.split(maxsplit=1)
        return parts[0].rstrip('.')
    
    def __create_section_entry(self, section_id: str, buffer: List[str]) -> Dict:
        content_text = " ".join(buffer).strip()
        
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "content": content_text
        }
    
    def __calculate_content_stats(self, sections: List[Dict]):
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
    
    def _get_parse_stats(self) -> Dict:
        base_stats = self._get_metadata()
        spec_stats = {
            "parser_type": self._parser_type,
            "total_content_length": self.__total_content_length,
            "sections_with_content": self.__sections_with_content,
            "avg_content_length": round(self.__avg_content_length, 2),
            "buffer_size": self._buffer_size
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