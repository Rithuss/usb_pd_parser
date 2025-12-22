"""
USB PD Parser Orchestrator

Coordinates the complete parsing pipeline using
composition and clean OOP design.
"""

import os
from datetime import datetime
from typing import Dict, List

import pdfplumber
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


from core.factories import ParserFactory, WriterFactory, ValidatorFactory
from parsers.usb_pd_toc_parser import USBPDTOCParser
from parsers.usb_pd_spec_parser import USBPDSpecParser
from writers.jsonl_writer import JSONLWriter
from writers.validation_report_writer import ValidationReportWriter
from strategies.toc_validation_strategy import TOCValidationStrategy
from strategies.spec_validation_strategy import SpecValidationStrategy


LOG_INTERVAL = 100


class ProgressTracker:
    """Tracks pipeline progress"""

    def __init__(self) -> None:
        self._total_steps = 6
        self._current_step = 0

    def start(self, name: str) -> None:
        self._current_step += 1
        print(f"\n[STEP {self._current_step}/{self._total_steps}] {name}")
        print("-" * 60)

    @staticmethod
    def done(message: str = "") -> None:
        if message:
            print(f"✓ {message}")


class StatisticsCollector:
    """Collects execution statistics"""

    def __init__(self) -> None:
        self._stats: Dict[str, Dict] = {}

    def record(self, key: str, value: Dict) -> None:
        self._stats[key] = value

    def get(self) -> Dict:
        return self._stats.copy()


class ComponentRegistry:
    """Registers all factories"""

    @staticmethod
    def register() -> None:
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)

        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer("validation", ValidationReportWriter)

        ValidatorFactory.register_validator("toc", TOCValidationStrategy)
        ValidatorFactory.register_validator("spec", SpecValidationStrategy)


class PDFTextExtractor:
    """Extracts text from PDF"""

    def __init__(self, pdf_path: str) -> None:
        self._pdf_path = pdf_path
        self.total_pages = 0
        self.pages_processed = 0

    def extract(self) -> Dict[int, str]:
        text_data: Dict[int, str] = {}

        with pdfplumber.open(self._pdf_path) as pdf:
            self.total_pages = len(pdf.pages)

            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text_data[index] = text

                if text:
                    self.pages_processed += 1

                if index % LOG_INTERVAL == 0:
                    print(f"  Processed: {index}/{self.total_pages}")

        return text_data


class USBPDParserOrchestrator:
    """Composition root of the application"""

    def __init__(self, pdf_path: str, output_dir: str) -> None:
        self._pdf_path = pdf_path
        self._output_dir = output_dir
        self._doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )

        self._parsers: Dict[str, object] = {}
        self._writers: Dict[str, object] = {}
        self._validators: Dict[str, object] = {}
        self._results: Dict[str, list] = {}

        self._progress = ProgressTracker()
        self._stats = StatisticsCollector()

        self._start_time: datetime | None = None
        self._end_time: datetime | None = None

    def initialize(self) -> None:
        ComponentRegistry.register()
        self._create_components()

    def _create_components(self) -> None:
        self._parsers["toc"] = ParserFactory.create_parser(
            "toc", self._doc_title
        )
        self._parsers["spec"] = ParserFactory.create_parser(
            "spec", self._doc_title
        )

        paths = self._output_paths()

        self._writers["toc"] = WriterFactory.create_writer(
            "jsonl", paths["toc"]
        )
        self._writers["spec"] = WriterFactory.create_writer(
            "jsonl", paths["spec"]
        )
        self._writers["report"] = WriterFactory.create_writer(
            "validation", paths["report"]
        )
        self._writers["summary"] = WriterFactory.create_writer(
            "validation", paths["summary"]
        )

        self._validators["toc"] = ValidatorFactory.create_validator("toc")
        self._validators["spec"] = ValidatorFactory.create_validator("spec")

    def execute(self) -> None:
        self.initialize()
        self._start_time = datetime.now()

        self._extract()
        self._parse()
        self._validate()
        self._write()
        self._report()

        self._end_time = datetime.now()
        self._print_summary()

    def _extract(self) -> None:
        self._progress.start("Extracting PDF Text")

        extractor = PDFTextExtractor(self._pdf_path)
        text_data = extractor.extract()

        self._stats.record(
            "extraction",
            {
                "total_pages": extractor.total_pages,
                "pages_processed": extractor.pages_processed,
            },
        )

        self._results["text"] = text_data

    def _parse(self) -> None:
        self._progress.start("Parsing TOC & Spec")

        toc = self._parsers["toc"].parse(self._results["text"])
        spec = self._parsers["spec"].parse(self._results["text"])

        self._results["toc"] = toc
        self._results["spec"] = spec

        self._stats.record(
            "parsing",
            {"toc": len(toc), "spec": len(spec)},
        )

    def _validate(self) -> None:
        self._progress.start("Validating Results")

        self._stats.record(
            "validation",
            {
                "toc": self._validators["toc"].validate(
                    self._results["toc"]
                ),
                "spec": self._validators["spec"].validate(
                    self._results["spec"]
                ),
            },
        )

    def _write(self) -> None:
        self._progress.start("Writing Outputs")

        self._writers["toc"].write(self._results["toc"])
        self._writers["spec"].write(self._results["spec"])

    def _report(self) -> None:
        self._progress.start("Generating Reports")

        report = {
            "document": self._doc_title,
            "statistics": self._stats.get(),
        }

        self._writers["report"].write(report)
        self._writers["summary"].write(report)

    def _output_paths(self) -> Dict[str, str]:
        return {
            "toc": os.path.join(self._output_dir, "usb_pd_toc.jsonl"),
            "spec": os.path.join(self._output_dir, "usb_pd_spec.jsonl"),
            "report": os.path.join(
                self._output_dir, "validation_report.json"
            ),
            "summary": os.path.join(
                self._output_dir, "execution_summary.json"
            ),
        }

    def _print_summary(self) -> None:
        duration = (
            self._end_time - self._start_time
        ).total_seconds()

        print("\n" + "=" * 60)
        print("EXECUTION COMPLETE")
        print(f"Duration: {duration:.2f}s")
        print("=" * 60)
