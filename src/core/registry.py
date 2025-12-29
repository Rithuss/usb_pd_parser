"""
Central registry loader.
Ensures all parsers, writers, and validators are registered.
"""

from .factories import ParserFactory, WriterFactory, ValidatorFactory

# Parsers
from src.parsers.pdf_parser import PDFParser
from src.parsers.usb_pd_toc_parser import USBPDTOCParser
from src.parsers.usb_pd_spec_parser import USBPDSpecParser

# Writers
from src.writers.jsonl_writer import JSONLWriter
from src.writers.validation_report_writer import ValidationReportWriter

# Validators
from src.strategies.toc_validation_strategy import TOCValidationStrategy
from src.strategies.spec_validation_strategy import SpecValidationStrategy


ParserFactory.register_parser("pdf", PDFParser)
ParserFactory.register_parser("toc", USBPDTOCParser)
ParserFactory.register_parser("spec", USBPDSpecParser)

WriterFactory.register_writer("jsonl", JSONLWriter)
WriterFactory.register_writer("validation", ValidationReportWriter)

ValidatorFactory.register_validator("toc", TOCValidationStrategy)
ValidatorFactory.register_validator("spec", SpecValidationStrategy)
