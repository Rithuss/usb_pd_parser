"""
USB PD Parser Orchestrator

Coordinates the full parsing pipeline using
Composition and Dependency Injection.
"""

from datetime import datetime
from typing import Dict

from ..core.factories import ParserFactory, WriterFactory, ValidatorFactory
from ..parsers.usb_pd_toc_parser import USBPDTOCParser
from ..parsers.usb_pd_spec_parser import USBPDSpecParser
from ..writers.jsonl_writer import JSONLWriter
from ..writers.validation_report_writer import ValidationReportWriter
from ..strategies.toc_validation_strategy import TOCValidationStrategy
from ..strategies.spec_validation_strategy import SpecValidationStrategy
from src.usb_pd_parser import PDFParser


class USBPDParserOrchestrator:
    """
    Composition root that coordinates all components.
    """

    def __init__(self, pdf_path: str, output_dir: str):
        self.__pdf_path = pdf_path
        self.__output_dir = output_dir
        self.__doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )

        self.__parsers: Dict[str, object] = {}
        self.__writers: Dict[str, object] = {}
        self.__validators: Dict[str, object] = {}
        self.__results: Dict[str, object] = {}

        self.__start_time = None
        self.__end_time = None

    # ---------- Initialization ----------

    def initialize(self) -> None:
        self._register_components()
        self._create_components()

    def _register_components(self) -> None:
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)

        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer(
            "validation",
            ValidationReportWriter,
        )

        ValidatorFactory.register_validator(
            "toc",
            TOCValidationStrategy,
        )
        ValidatorFactory.register_validator(
            "spec",
            SpecValidationStrategy,
        )

    def _create_components(self) -> None:
        self.__parsers["toc"] = ParserFactory.create_parser(
            "toc", self.__doc_title
        )
        self.__parsers["spec"] = ParserFactory.create_parser(
            "spec", self.__doc_title
        )

        self.__writers["toc"] = WriterFactory.create_writer(
            "jsonl",
            f"{self.__output_dir}/usb_pd_toc.jsonl",
        )
        self.__writers["spec"] = WriterFactory.create_writer(
            "jsonl",
            f"{self.__output_dir}/usb_pd_spec.jsonl",
        )
        self.__writers["report"] = WriterFactory.create_writer(
            "validation",
            f"{self.__output_dir}/validation_report.json",
        )

        self.__validators["toc"] = (
            ValidatorFactory.create_validator("toc")
        )
        self.__validators["spec"] = (
            ValidatorFactory.create_validator("spec")
        )

    # ---------- Execution Pipeline ----------

    def execute(self) -> None:
        self.initialize()
        self.__start_time = datetime.now()

        text_data = self._extract()
        self._parse(text_data)
        self._validate()
        self._write()

        self.__end_time = datetime.now()
        self._print_summary()

    # ---------- Pipeline Steps ----------

    def _extract(self) -> Dict[int, str]:
        parser = PDFParser(self.__pdf_path)
        return parser.extract_text()


    def _parse(self, text_data: Dict[int, str]) -> None:
        self.__results["toc"] = self.__parsers["toc"].parse(text_data)
        self.__results["spec"] = self.__parsers["spec"].parse(text_data)

    def _validate(self) -> None:
        self.__validators["toc"].validate(
            self.__results["toc"]
        )
        self.__validators["spec"].validate(
            self.__results["spec"]
        )

    def _write(self) -> None:
        self.__writers["toc"].write(self.__results["toc"])
        self.__writers["spec"].write(self.__results["spec"])

        report = {
            "document": self.__doc_title,
            "execution_time": self._execution_time(),
        }
        self.__writers["report"].write(report)

    # ---------- Helpers ----------

    def _execution_time(self) -> float:
        if not self.__start_time or not self.__end_time:
            return 0.0
        return (
            self.__end_time - self.__start_time
        ).total_seconds()


    def _print_summary(self) -> None:
        print("\n✓ EXECUTION COMPLETED")
        print(f"Duration: {self._execution_time():.2f}s")
      