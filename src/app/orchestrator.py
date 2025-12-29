from datetime import datetime
from typing import Dict, Any

from ..core.factories import ParserFactory, WriterFactory, ValidatorFactory
from ..core.interfaces import Parseable, Writeable, Validatable
from ..core import registry  # noqa: F401  ← IMPORTANT


class USBPDParserOrchestrator:
    """Composition root coordinating the parsing pipeline."""

    def __init__(self, pdf_path: str, output_dir: str):
        self.__pdf_path = pdf_path
        self.__output_dir = output_dir
        self.__doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )

        self.__parsers: Dict[str, Parseable] = {}
        self.__writers: Dict[str, Writeable] = {}
        self.__validators: Dict[str, Validatable] = {}
        self.__results: Dict[str, Any] = {}

        self.__start_time = None
        self.__end_time = None

    def initialize(self) -> None:
        self.__parsers["pdf"] = ParserFactory.create_parser(
            "pdf",
            self.__pdf_path,
        )
        self.__parsers["toc"] = ParserFactory.create_parser(
            "toc",
            self.__doc_title,
        )
        self.__parsers["spec"] = ParserFactory.create_parser(
            "spec",
            self.__doc_title,
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

        self.__validators["toc"] = ValidatorFactory.create_validator("toc")
        self.__validators["spec"] = ValidatorFactory.create_validator("spec")

    def execute(self) -> None:
        self.initialize()
        self.__start_time = datetime.now()

        text_data = self.__parsers["pdf"].extract_text()
        self.__results["toc"] = self.__parsers["toc"].parse(text_data)
        self.__results["spec"] = self.__parsers["spec"].parse(text_data)

        self.__validators["toc"].validate(self.__results["toc"])
        self.__validators["spec"].validate(self.__results["spec"])

        self.__writers["toc"].write(self.__results["toc"])
        self.__writers["spec"].write(self.__results["spec"])

        self.__writers["report"].write(
            {
                "document": self.__doc_title,
                "execution_time": self.__execution_time(),
            }
        )

        self.__end_time = datetime.now()
        self.__print_summary()

    def __execution_time(self) -> float:
        if not self.__start_time or not self.__end_time:
            return 0.0
        return (self.__end_time - self.__start_time).total_seconds()

    def __print_summary(self) -> None:
        print("\n✓ EXECUTION COMPLETED")
        print(f"Duration: {self.__execution_time():.2f}s")
