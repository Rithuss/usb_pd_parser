"""
USB PD Table of Contents Parser - REFACTORED
Fixed: parse() from 53 lines to 12 lines
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from core.base_classes import BaseParser


class USBPDTOCParser(BaseParser):
    
    def __init__(self, doc_title: str):
        super().__init__(doc_title)
        
        self.__toc_entries = []
        self.__hierarchy_levels = {}
        self.__max_depth = 0
        
        self._parser_type = "TOC"
        self._pattern_matched = 0
    
    @property
    def toc_entries(self) -> List[Dict]:
        return self.__toc_entries.copy()
    
    @property
    def max_depth(self) -> int:
        return self.__max_depth
    
    @property
    def hierarchy_levels(self) -> Dict[int, int]:
        return self.__hierarchy_levels.copy()
    
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        entries = []
        
        for page_num, content in text_data.items():
            if content:
                self._extract_page_entries(page_num, content, entries)
        
        self.__toc_entries = entries
        self._mark_as_parsed(entries)
        
        return entries
    
    def _extract_page_entries(self, page_num: int, content: str, entries: list):
        for line in content.split("\n"):
            entry = self.__parse_toc_line(line, page_num)
            if entry:
                entries.append(entry)
                self._pattern_matched += 1
                self._update_hierarchy(entry)
    
    def _update_hierarchy(self, entry: dict):
        level = entry["level"]
        self.__hierarchy_levels[level] = self.__hierarchy_levels.get(level, 0) + 1
        self.__max_depth = max(self.__max_depth, level)
    
    def validate(self) -> bool:
        if not self.is_parsed:
            return False
        
        if self.total_items == 0:
            return False
        
        if self.__max_depth < 1 or self.__max_depth > 10:
            return False
        
        return True
    
    def __parse_toc_line(self, line: str, page_num: int):
        line_stripped = line.strip()
        
        if not line_stripped:
            return None
        
        if not (line_stripped and line_stripped[0].isdigit()):
            return None
        
        parts = line_stripped.split(maxsplit=1)
        section_id = parts[0].rstrip('.')
        title = parts[1] if len(parts) > 1 else ""
        
        level = section_id.count('.') + 1
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
    
    def __calculate_parent_id(self, section_id: str):
        if '.' not in section_id:
            return None
        
        parts = section_id.split('.')
        parent_parts = parts[:-1]
        return '.'.join(parent_parts)
    
    def _get_parse_stats(self) -> Dict:
        base_stats = self._get_metadata()
        toc_stats = {
            "parser_type": self._parser_type,
            "pattern_matched": self._pattern_matched,
            "max_depth": self.__max_depth,
            "hierarchy_levels": self.__hierarchy_levels
        }
        
        return {**base_stats, **toc_stats}
    
    def __iter__(self):
        return iter(self.__toc_entries)
    
    def __getitem__(self, index: int) -> Dict:
        return self.__toc_entries[index]
    
    def __contains__(self, section_id: str) -> bool:
        return any(
            entry["section_id"] == section_id
            for entry in self.__toc_entries
        )


if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("toc", USBPDTOCParser)