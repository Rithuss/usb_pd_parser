"""
Validation Report Writer
Writes validation reports in JSON format.

OOP Concepts:
- INHERITANCE: Inherits from BaseOutputWriter
- POLYMORPHISM: Different write() implementation
- ENCAPSULATION: Private formatting logic
"""

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from src.core.base_classes import BaseOutputWriter


class ValidationReportWriter(BaseOutputWriter):
    """
    Validation report writer (JSON format).

    OOP Principles:
    - INHERITANCE: Extends BaseOutputWriter
    - POLYMORPHISM: Custom write() for reports
    - ENCAPSULATION: Private report formatting
    """

    def __init__(self, output_path: str):
        """
        Initialize validation report writer.

        Args:
            output_path: Path to output file
        """
        super().__init__(output_path)

        # PRIVATE ATTRIBUTES (Encapsulation)
        self.__report_data: Dict[str, Any] = {}
        self.__generation_time = None
        self.__report_size = 0

        # PROTECTED CONFIGURATION
        self._format_name = "JSON"
        self._indent = 2
        self._encoding = "utf-8"
        self._ensure_ascii = False

    # -------------------- PROPERTIES --------------------

    @property
    def report_data(self) -> Dict[str, Any]:
        """Return written report data (read-only)."""
        return self.__report_data.copy()

    @property
    def generation_time(self) -> str | None:
        """Return report generation time."""
        return (
            self.__generation_time.isoformat()
            if self.__generation_time
            else None
        )

    @property
    def report_size(self) -> int:
        """Return report size in bytes."""
        return self.__report_size

    # -------------------- POLYMORPHISM --------------------

    def write(self, data: Dict[str, Any]) -> bool:
        """
        Write validation report to JSON file.

        Args:
            data: Validation report dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            enhanced_report = self.__enhance_report(data)
            self.__ensure_directory()

            json_str = json.dumps(
                enhanced_report,
                indent=self._indent,
                ensure_ascii=self._ensure_ascii,
            )

            with open(
                self.output_path,
                "w",
                encoding=self._encoding,
            ) as file:
                file.write(json_str)

            self.__report_size = len(
                json_str.encode(self._encoding)
            )
            self.__report_data = enhanced_report
            self.__generation_time = datetime.now()

            self._lines_written += 1
            return True

        except Exception as exc:
            print(f"Error writing report: {exc}")
            return False

    # -------------------- PRIVATE HELPERS --------------------

    def __enhance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance report with metadata."""
        enhanced = data.copy()

        metadata = enhanced.setdefault("metadata", {})
        metadata["generated_at"] = datetime.now().isoformat()
        metadata["output_path"] = self.output_path
        metadata["format"] = self._format_name

        return enhanced

    def __ensure_directory(self) -> None:
        """Ensure output directory exists."""
        Path(self.output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    # -------------------- PROTECTED HELPERS --------------------

    def _get_report_stats(self) -> Dict[str, Any]:
        """Return report writing statistics."""
        base_stats = self._get_write_stats()
        report_stats = {
            "format": self._format_name,
            "report_size": self.__report_size,
            "generation_time": self.generation_time,
        }
        return {**base_stats, **report_stats}

    # -------------------- PUBLIC VALIDATION --------------------

    def validate_report(self, data: Dict[str, Any]) -> bool:
        """Validate report structure before writing."""
        required_keys = {
            "document",
            "summary",
            "validation_status",
        }
        return required_keys.issubset(data)

    # -------------------- SPECIAL METHODS --------------------

    def __str__(self) -> str:
        return (
            f"ValidationReportWriter("
            f"path='{self.output_path}', "
            f"size={self.__report_size}B)"
        )


# Factory registration
if __name__ != "__main__":
    from src.core.factories import WriterFactory

    WriterFactory.register_writer(
        "validation",
        ValidationReportWriter,
    )
