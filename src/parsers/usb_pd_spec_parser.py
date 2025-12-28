"""
USB PD Specification Content Parser
Parses specification section content from the document.
"""

from typing import Dict, List, Optional
from src.core.base_classes import BaseParser



class USBPDSpecParser(BaseParser):
    """
    Concrete parser for extracting specification content.
    Demonstrates clean OOP and modular parsing.
    """

    _MIN_CONTENT_RATIO = 0.5

    def __init__(self, doc_title: str):
        super().__init__(doc_title)

        # Private state
        self.__sections: List[Dict] = []
        self.__sections_with_content = 0

    # ---------- Properties ----------

    @property
    def content_sections(self) -> List[Dict]:
        return self.__sections.copy()

    # ---------- Public API ----------

    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse specification sections from extracted text.
        """
        sections: List[Dict] = []
        current_id: Optional[str] = None
        buffer: List[str] = []

        for content in text_data.values():
            if content:
                current_id, buffer = self._process_page(
                    content,
                    sections,
                    current_id,
                    buffer,
                )

        self._finalize_section(sections, current_id, buffer)
        self._update_stats(sections)

        self.__sections = sections
        self._mark_as_parsed(sections)
        return sections

    def validate(self) -> bool:
        """
        Validate parsed specification content.
        """
        if not self.is_parsed or self.total_items == 0:
            return False

        ratio = self.__sections_with_content / self.total_items
        return ratio >= self._MIN_CONTENT_RATIO

    # ---------- Protected Helpers ----------

    def _process_page(
        self,
        content: str,
        sections: List[Dict],
        current_id: Optional[str],
        buffer: List[str],
    ) -> tuple[Optional[str], List[str]]:
        for line in content.splitlines():
            line = line.strip()

            if self._is_section_header(line):
                current_id, buffer = self._start_section(
                    sections,
                    current_id,
                    buffer,
                    line,
                )
            elif line:
                buffer.append(line)

        return current_id, buffer

    def _start_section(
        self,
        sections: List[Dict],
        current_id: Optional[str],
        buffer: List[str],
        line: str,
    ) -> tuple[str, List[str]]:
        if current_id and buffer:
            sections.append(
                self._build_section(current_id, buffer)
            )

        section_id, title = self._extract_header(line)
        return section_id, [title] if title else []

    def _finalize_section(
        self,
        sections: List[Dict],
        current_id: Optional[str],
        buffer: List[str],
    ) -> None:
        if current_id and buffer:
            sections.append(
                self._build_section(current_id, buffer)
            )

    def _is_section_header(self, line: str) -> bool:
        return bool(line) and line[0].isdigit()

    def _extract_header(self, line: str) -> tuple[str, str]:
        parts = line.split(maxsplit=1)
        section_id = parts[0].rstrip(".")
        title = parts[1] if len(parts) > 1 else ""
        return section_id, title

    def _build_section(
        self,
        section_id: str,
        buffer: List[str],
    ) -> Dict:
        content = " ".join(buffer).strip()
        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "content": content,
        }

    def _update_stats(self, sections: List[Dict]) -> None:
        self.__sections_with_content = sum(
            1
            for section in sections
            if section.get("content", "").strip()
        )

    # ---------- Special Methods ----------

    def __len__(self) -> int:
        return len(self.__sections)

    def __iter__(self):
        return iter(self.__sections)

    def __str__(self) -> str:
        return (
            f"USBPDSpecParser("
            f"sections={len(self)}, "
            f"with_content={self.__sections_with_content})"
        )
