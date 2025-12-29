"""
USB Power Delivery Specification Parser - REFACTORED
Evaluation-aligned OOP version
"""

from src.core.base_classes import BaseParser

import json
import os
import pdfplumber
from typing import Dict, List, Any
from datetime import datetime


# ============================================================================
# HELPER CLASSES
# ============================================================================

class PageTracker:
    """Tracks page extraction statistics"""

    def __init__(self):
        self.total_pages = 0
        self.pages_with_content = 0
        self.pages_without_content = 0

    def increment_with_content(self):
        self.pages_with_content += 1

    def increment_without_content(self):
        self.pages_without_content += 1

    def get_coverage_percentage(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return round(
            (self.pages_with_content / self.total_pages) * 100, 2
        )

    def get_stats(self) -> Dict:
        return {
            "total_pages": self.total_pages,
            "pages_covered": self.pages_with_content,
            "pages_missing": self.pages_without_content,
            "coverage_percentage": self.get_coverage_percentage(),
        }


class SectionBuffer:
    """Buffers section content"""

    def __init__(self):
        self.current_section = None
        self.buffer: List[str] = []

    def start_new_section(self, section_id: str):
        self.current_section = section_id
        self.buffer = []

    def add_line(self, line: str):
        if line.strip():
            self.buffer.append(line.strip())

    def get_content(self) -> str:
        return " ".join(self.buffer).strip()

    def has_content(self) -> bool:
        return bool(self.get_content())


class ProgressPrinter:
    """Console output helper"""

    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)

    @staticmethod
    def print_step(step: int, total: int, desc: str):
        print(f"\n[STEP {step}/{total}] {desc}...")

    @staticmethod
    def print_success(msg: str):
        print(f"✓ {msg}")



# ============================================================================
# TOC PARSER
# ============================================================================

class USBPDTOCParser(BaseParser):
    """TOC parser"""

    def __init__(self, text_data: Dict[int, str], doc_title: str):
        super().__init__(doc_title)
        self._text_data = text_data
        self._results: List[Dict] = []

    def parse(self, data: Any = None) -> List[Dict]:
        self._results = []

        for page_num, content in self._text_data.items():
            if content:
                self._extract_from_page(page_num, content)

        self._mark_as_parsed(self._results)
        return self._results

    def _extract_from_page(self, page_num: int, content: str):
        for line in content.split("\n"):
            entry = self._parse_line(line, page_num)
            if entry:
                self._results.append(entry)

    def _parse_line(self, line: str, page_num: int) -> Dict | None:
        line = line.strip()
        if not line or not line[0].isdigit():
            return None

        parts = line.split(maxsplit=1)
        section_id = parts[0].rstrip(".")
        title = parts[1] if len(parts) > 1 else ""

        return {
            "doc_title": self.doc_title,
            "section_id": section_id,
            "title": title,
            "page": page_num,
            "level": section_id.count(".") + 1,
            "parent_id": self._parent_id(section_id),
        }

    def _parent_id(self, section_id: str) -> str | None:
        if "." not in section_id:
            return None
        return ".".join(section_id.split(".")[:-1])


# ============================================================================
# SPEC CONTENT PARSER
# ============================================================================

class USBPDSpecParser(BaseParser):
    """Specification content parser"""

    def __init__(self, text_data: Dict[int, str], doc_title: str):
        super().__init__(doc_title)
        self._text_data = text_data
        self._buffer = SectionBuffer()
        self._results: List[Dict] = []

    def parse(self, data: Any = None) -> List[Dict]:
        self._results = []

        for content in self._text_data.values():
            if content:
                self._process_page(content)

        self._save_section()
        self._mark_as_parsed(self._results)
        return self._results

    def _process_page(self, content: str):
        for line in content.split("\n"):
            self._process_line(line)

    def _process_line(self, line: str):
        line = line.strip()
        if not line:
            return

        if line[0].isdigit():
            self._save_section()
            section_id = line.split(maxsplit=1)[0].rstrip(".")
            self._buffer.start_new_section(section_id)
        else:
            self._buffer.add_line(line)

    def _save_section(self):
        if self._buffer.current_section and self._buffer.has_content():
            self._results.append(
                {
                    "doc_title": self.doc_title,
                    "section_id": self._buffer.current_section,
                    "content": self._buffer.get_content(),
                }
            )


# ============================================================================
# VALIDATION REPORT
# ============================================================================

class ValidationReportGenerator:
    """Generates validation metrics"""

    def __init__(
        self,
        toc: List[Dict],
        content: List[Dict],
        page_stats: Dict,
        doc_title: str,
    ):
        self._toc = toc
        self._content = content
        self._page_stats = page_stats
        self._doc_title = doc_title

    def generate_report(self) -> Dict:
        return {
            "document": self._doc_title,
            "timestamp": datetime.now().isoformat(),
            "toc_sections": len(self._toc),
            "content_sections": len(self._content),
            "page_coverage": self._page_stats,
        }



    