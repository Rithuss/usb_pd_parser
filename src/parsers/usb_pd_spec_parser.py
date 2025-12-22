"""
USB PD Specification Content Parser
Parses specification section content from the document.
"""

from typing import Dict, List, Optional, Tuple
from core.base_classes import BaseParser


class USBPDSpecParser(BaseParser):
    """
    Parser for extracting specification content sections.
    """

    _MIN_CONTENT_RATIO = 0.5

    def __init__(self, doc_title: str):
        super().__init__(doc_title)

        self.__sections: List[Dict] = []
        self.__total_content_length = 0
        self.__sections_with_content = 0
        self.__avg_content_length = 0.0

    # --------------------
    # Public API
    # --------------------
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse specification content from extracted text.
        """
        sections: List[Dict] = []
        current_section: Optional[str] = None
        buffer: List[str] = []

        for content in text_data.values():
            if content:
                current_section, buffer = self._parse_page(
                    content, sections, current_section, buffer
                )

        self._finalize(sections, current_section, buffer)
        self._calculate_stats(sections)

        self.__sections = sections
        self._mark_as_parsed(sections)
        return sections

    def validate(self) -> bool:
        """
        Validate parsed specification content.
        """
        if not self.is_parsed or self.total_items == 0:
            return False

        content_ratio = (
            self.__sections_with_content / self.total_items
        )
        return content_ratio >= self._MIN_CONTENT_RATIO

    # --------------------
    # Internal helpers
    # --------------------
    def _parse_page(
        self,
        content: str,
        sections: List[Dict],
        current_section: Optional[str],
        buffer: List[str],
    ) -> Tuple[Optional[str], List[str]]:
        for line in content.splitlines():
            line = line.strip()

            if self._is_header(line):
                current_section, buffer = self._start_new_section(
                    sections, current_section, buffer, line
                )
            elif line:
                buffer.append(line)

        return current_section, buffer

    def _start_new_section(
        self,
        sections: List[Dict],
        current_section: Optional[str],
        buffer: List[str],
        line: str,
    ) -> Tuple[str, List[str]]:
        if current_section and buffer:
            sections.append(
                self._create_entry(current_section, buffer)
            )

        section_id, title = self._split_header(line)
        return section_id, [title] if title else []

    def _finalize(
        self,
        sections: List[Dict],
        current_section: Optional[str],
        buffer: List[str],
    ) -> None:
        if current_section and buffer:
            sections.append(
                self._create_entry(current_section, buffer)
            )

    def _is_header(self, line: str) -> bool:
        return bool(line) and line[0].isdigit()

    def _split_header(self, line: str) -> Tuple[str, str]:
        parts = line.split(maxsplit=1)
        section_id = parts[0].rstrip(".")
        title = parts[1] if len(parts) > 1 else ""
        return section_id, title

    def _create_entry(
        self,
        section_id: str,
        buffer: List[str],
    ) -> Dict:
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "content": " ".join(buffer).strip(),
        }

    def _calculate_stats(self, sections: List[Dict]) -> None:
        self.__total_content_length = sum(
            len(s.get("content", ""))
            for s in sections
        )

        self.__sections_with_content = sum(
            1
            for s in sections
            if s.get("content", "").strip()
        )

        self.__avg_content_length = (
            self.__total_content_length / len(sections)
            if sections else 0.0
        )

    # --------------------
    # Properties
    # --------------------
    @property
    def content_sections(self) -> List[Dict]:
        return self.__sections.copy()

    @property
    def avg_content_length(self) -> float:
        return self.__avg_content_length
