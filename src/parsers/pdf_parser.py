import pdfplumber
from typing import Dict

from src.core.factories import ParserFactory


class PageTracker:
    """Tracks page extraction statistics."""

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
            (self.pages_with_content / self.total_pages) * 100,
            2,
        )

    def get_stats(self) -> Dict:
        return {
            "total_pages": self.total_pages,
            "pages_covered": self.pages_with_content,
            "pages_missing": self.pages_without_content,
            "coverage_percentage": self.get_coverage_percentage(),
        }


class ProgressPrinter:
    """Console output helper."""

    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)


class PDFParser:
    """Extracts raw text from PDF."""

    def __init__(self, pdf_path: str):
        self._pdf_path = pdf_path
        self._tracker = PageTracker()
        self._printer = ProgressPrinter()

    def extract_text(self) -> Dict[int, str]:
        self._printer.print_header("PDF EXTRACTION STARTED")

        text_data: Dict[int, str] = {}

        with pdfplumber.open(self._pdf_path) as pdf:
            self._tracker.total_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text_data[i] = text

                if text.strip():
                    self._tracker.increment_with_content()
                else:
                    self._tracker.increment_without_content()

        stats = self._tracker.get_stats()
        print(f"Pages covered: {stats['coverage_percentage']}%")

        return text_data

    def get_page_coverage_stats(self) -> Dict:
        return self._tracker.get_stats()


# ✅ Factory registration (SIDE EFFECT)
ParserFactory.register_parser("pdf", PDFParser)
