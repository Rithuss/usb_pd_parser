"""USB PD specification content parser."""

import sys
import os
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from typing import Dict, List
from core.base_classes import BaseParser


class ParsingState:
    def __init__(self):
        self.current_section = None
        self.current_title = None
        self.current_page = None
        self.buffer = ContentBuffer()


class SectionDetector:
    @staticmethod
    def is_section_header(line: str) -> bool:
        if not line:
            return False
        return line[0].isdigit()

    @staticmethod
    def extract_section_id(line: str) -> str:
        parts = line.split(maxsplit=1)
        return parts[0].rstrip('.')

    @staticmethod
    def extract_section_title(line: str) -> str:
        parts = line.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""


class ContentBuffer:
    def __init__(self):
        self.buffer = []

    def add(self, text: str):
        self.buffer.append(text)

    def get_content(self) -> str:
        return " ".join(self.buffer).strip()

    def clear(self):
        self.buffer = []


class ParsingStats:
    def __init__(self):
        self.total_length = 0
        self.sections_with_content = 0
        self.avg_length = 0.0

    def calculate(self, sections: List[Dict]):
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

    def __init__(self, doc_title: str):
        super().__init__(doc_title)
        self._detector = SectionDetector()
        self._sections = []
        self._state = ParsingState()
        self._stats = ParsingStats()
    
    @property
    def total_content_length(self) -> int:
        return self._stats.total_length

    @property
    def avg_content_length(self) -> float:
        return self._stats.avg_length

    @property
    def content_sections(self):
        return self._sections
    

    def parse(self, text_data: Dict[int, str]) -> List[Dict]:

        self._sections = []
        self._state = ParsingState()

        for page_num, content in text_data.items():
            if not content:
                continue
            self._process_page_content(content, page_num)

        self._save_section()
        self._stats.calculate(self._sections)
        self._mark_as_parsed(self._sections)

        return self._sections

    def _process_page_content(self, content: str, page_num: int):
        lines = content.split("\n")
        for line in lines:
            self._handle_content_line(line.strip(), page_num)

    def _handle_content_line(self, line_stripped: str, page_num: int):
        if self._detector.is_section_header(line_stripped):
            self._save_section()
            section_id, title = self._start_new_section(line_stripped)
            self._state.current_section = section_id
            self._state.current_title = title
            self._state.current_page = page_num
        else:
            if line_stripped:
                self._state.buffer.add(line_stripped)

    def _start_new_section(self, line: str) -> tuple:
        section_id = self._detector.extract_section_id(line)
        title = self._detector.extract_section_title(line)
        return section_id, title

    def _calculate_section_level(self, section_id: str) -> int:
        if not section_id:
            return 0
        return section_id.count('.') + 1

    def _get_parent_id(self, section_id: str) -> str:
        if not section_id or '.' not in section_id:
            return None
        return '.'.join(section_id.split('.')[:-1])

    def _save_section(self):
        section_id = self._state.current_section
        if section_id:
            title = self._state.current_title
            page_num = self._state.current_page
            content_text = self._state.buffer.get_content()

            section_record = {
                "doc_title": self.doc_title,
                "section_id": section_id,
                "title": title if title else "",
                "page": page_num if page_num else 0,
                "level": self._calculate_section_level(section_id),
                "parent_id": self._get_parent_id(section_id),
                "content": content_text
            }

            self._sections.append(section_record)
            self._state.buffer.clear()

    def validate(self) -> bool:
        return True

    def __iter__(self):
        return iter(self._sections)

    def __getitem__(self, index: int) -> Dict: 
        return self._sections[index]

    def __contains__(self, section_id: str) -> bool:
        return any(
            entry["section_id"] == section_id
            for entry in self._sections
        )


if __name__ != "__main__":
    from core.factories import ParserFactory
    ParserFactory.register_parser("spec", USBPDSpecParser)