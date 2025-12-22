"""
USB PD Table of Contents Parser
Parses TOC sections from USB PD specification.
"""

from typing import Dict, List, Optional
from core.base_classes import BaseParser


class USBPDTOCParser(BaseParser):
    """
    Parser for extracting Table of Contents entries.
    Demonstrates clean parsing logic with low complexity.
    """

    _MIN_DEPTH = 1
    _MAX_DEPTH = 10

    def __init__(self, doc_title: str):
        super().__init__(doc_title)

        self.__entries: List[Dict] = []
        self.__max_depth: int = 0

    # --------------------
    # Public API
    # --------------------
    def parse(self, text_data: Dict[int, str]) -> List[Dict]:
        """
        Parse TOC entries from extracted PDF text.
        """
        entries: List[Dict] = []

        for page_num, content in text_data.items():
            if content:
                self._parse_page(content, page_num, entries)

        self.__entries = entries
        self._mark_as_parsed(entries)
        return entries

    def validate(self) -> bool:
        """
        Basic validation for parsed TOC data.
        """
        if not self.is_parsed or self.total_items == 0:
            return False

        return self._MIN_DEPTH <= self.__max_depth <= self._MAX_DEPTH

    # --------------------
    # Internal helpers
    # --------------------
    def _parse_page(
        self,
        content: str,
        page_num: int,
        entries: List[Dict],
    ) -> None:
        for line in content.splitlines():
            entry = self._parse_line(line, page_num)
            if entry:
                entries.append(entry)
                self._update_depth(entry["level"])

    def _parse_line(
        self,
        line: str,
        page_num: int,
    ) -> Optional[Dict]:
        line = line.strip()

        if not line or not line[0].isdigit():
            return None

        section_id, title = self._split_line(line)
        level = section_id.count(".") + 1

        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "title": title,
            "page": page_num,
            "level": level,
            "parent_id": self._get_parent_id(section_id),
            "full_path": f"{section_id} {title}",
        }

    def _split_line(self, line: str) -> tuple[str, str]:
        parts = line.split(maxsplit=1)
        section_id = parts[0].rstrip(".")
        title = parts[1] if len(parts) > 1 else ""
        return section_id, title

    def _get_parent_id(self, section_id: str) -> Optional[str]:
        if "." not in section_id:
            return None
        return ".".join(section_id.split(".")[:-1])

    def _update_depth(self, level: int) -> None:
        self.__max_depth = max(self.__max_depth, level)

    # --------------------
    # Properties
    # --------------------
    @property
    def max_depth(self) -> int:
        return self.__max_depth

    @property
    def toc_entries(self) -> List[Dict]:
        return self.__entries.copy()
