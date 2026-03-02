"""USB PD parser orchestrator components.

Coordinates the complete parsing pipeline: component registration,
PDF extraction, parsing, validation, output writing, and reporting.
"""
import sys
import os
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import pdfplumber
from typing import Dict, List
from pathlib import Path
from datetime import datetime

from core.factories import (
    ParserFactory,
    WriterFactory,
    ValidatorFactory
)
from parsers.usb_pd_toc_parser import USBPDTOCParser
from parsers.usb_pd_spec_parser import USBPDSpecParser
from writers.jsonl_writer import JSONLWriter
from writers.validation_report_writer import ValidationReportWriter
from strategies.toc_validation_strategy import (
    TOCValidationStrategy
)
from strategies.spec_validation_strategy import (
    SpecValidationStrategy
)


class ComponentRegistrar:
    """Registers all available components with their factories.
    
    Centralizes registration of parsers, writers, and validators
    so they can be created by name throughout the application.
    """
    
    @staticmethod
    def register_all():
        """Register all parsers, writers, and validators."""
        ComponentRegistrar._register_parsers()
        ComponentRegistrar._register_writers()
        ComponentRegistrar._register_validators()
    
    @staticmethod
    def _register_parsers():
        """Register parser classes with the factory."""
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)
    
    @staticmethod
    def _register_writers():
        """Register writer classes with the factory."""
        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer(
            "validation",
            ValidationReportWriter
        )
    
    @staticmethod
    def _register_validators():
        """Register validator classes with the factory."""
        ValidatorFactory.register_validator(
            "toc",
            TOCValidationStrategy
        )
        ValidatorFactory.register_validator(
            "spec",
            SpecValidationStrategy
        )


class ComponentFactory:
    """Creates configured instances of parsers, writers, and validators.
    
    Uses document title and output directory to set up components
    properly for the parsing pipeline.
    """
    
    def __init__(self, doc_title: str, output_dir: str):
        self.doc_title = doc_title
        self.output_dir = output_dir
    
    def create_parsers(self) -> Dict:
        """Create and return parser instances."""
        return {
            "toc": self._create_toc_parser(),
            "spec": self._create_spec_parser()
        }
    
    def create_writers(self) -> Dict:
        """Create and return writer instances."""
        return {
            "toc": self._create_toc_writer(),
            "spec": self._create_spec_writer(),
            "report": self._create_report_writer()
        }
    
    def create_validators(self) -> Dict:
        """Create and return validator instances."""
        return {
            "toc": self._create_toc_validator(),
            "spec": self._create_spec_validator()
        }
    
    def _create_toc_parser(self):
        """Create a TOC parser instance."""
        return ParserFactory.create_parser("toc", self.doc_title)
    
    def _create_spec_parser(self):
        """Create a spec parser instance."""
        return ParserFactory.create_parser("spec", self.doc_title)
    
    def _create_toc_writer(self):
        """Create a TOC writer instance."""
        return WriterFactory.create_writer(
            "jsonl",
            os.path.join(self.output_dir, "usb_pd_toc.jsonl")
        )
    
    def _create_spec_writer(self):
        """Create a spec writer instance."""
        return WriterFactory.create_writer(
            "jsonl",
            os.path.join(self.output_dir, "usb_pd_spec.jsonl")
        )
    
    def _create_report_writer(self):
        """Create a report writer instance."""
        return WriterFactory.create_writer(
            "validation",
            os.path.join(
                self.output_dir,
                "validation_report.json"
            )
        )
    
    def _create_toc_validator(self):
        """Create a TOC validator instance."""
        return ValidatorFactory.create_validator("toc")
    
    def _create_spec_validator(self):
        """Create a spec validator instance."""
        return ValidatorFactory.create_validator("spec")


class PDFExtractor:
    """Extracts text from PDF pages.
    
    Opens PDF files, extracts text from each page, and tracks
    coverage statistics for reporting.
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0
        self.pages_processed = 0
    
    def extract(self) -> Dict[int, str]:
        """Extract text from all PDF pages.
        
        Returns dictionary mapping page numbers to extracted text.
        """
        print("\n[STEP 1] Extracting PDF Text...")
        print("-" * 60)
        
        text_data = {}
        
        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)
            self._print_extraction_start()
            
            text_data = self._process_pages(pdf.pages)
        
        self._print_summary()
        return text_data
    
    def _print_extraction_start(self):
        """Print initial extraction information."""
        print(f"Total pages: {self.total_pages}")
    
    def _process_pages(self, pages) -> Dict[int, str]:
        """Process each page to extract text."""
        text_data = {}
        
        for i, page in enumerate(pages, start=1):
            text = page.extract_text()
            text_data[i] = text if text else ""
            
            if text:
                self.pages_processed += 1
            
            self._print_progress(i)
        
        return text_data
    
    def _print_progress(self, current_page: int):
        """Print progress update every 100 pages."""
        if current_page % 100 == 0:
            print(f"  Processed: {current_page}/{self.total_pages}")
    
    def _print_summary(self):
        """Print extraction results and coverage."""
        coverage = (self.pages_processed / self.total_pages * 100)
        print(f"\n✓ Extraction Complete:")
        print(f"  Pages processed: {self.pages_processed}")
        print(f"  Coverage: {coverage:.1f}%")
    
    def get_coverage(self) -> float:
        """Get percentage of pages with extracted text."""
        if self.total_pages > 0:
            return (self.pages_processed / self.total_pages * 100)
        return 0


class ParsingCoordinator:
    """Coordinates TOC and content parsing.
    
    Uses parser instances to extract TOC entries and content sections
    from text data, then returns the results.
    """
    
    def __init__(self, parsers: Dict, text_data: Dict[int, str]):
        self.parsers = parsers
        self.text_data = text_data
        self.results = {}
    
    def parse_toc(self) -> List[Dict]:
        """Run TOC parser and return results."""
        print("\n[STEP 2] Parsing Table of Contents...")
        print("-" * 60)
        
        toc_parser = self.parsers["toc"]
        toc_data = toc_parser.parse(self.text_data)
        self.results["toc"] = toc_data
        
        self._print_toc_parse_summary(toc_parser)
        
        return toc_data
    
    def parse_content(self) -> List[Dict]:
        """Run content parser and return results."""
        print("\n[STEP 3] Parsing Specification Content...")
        print("-" * 60)
        
        spec_parser = self.parsers["spec"]
        spec_data = spec_parser.parse(self.text_data)
        self.results["spec"] = spec_data
        
        self._print_spec_parse_summary(spec_parser)
        
        return spec_data
    
    def _print_toc_parse_summary(self, toc_parser):
        """Print TOC parsing results."""
        print(f"✓ TOC Parsed:")
        print(f"  Sections: {len(toc_parser)}")
        print(f"  Max depth: {toc_parser.max_depth}")
    
    def _print_spec_parse_summary(self, spec_parser):
        """Print content parsing results."""
        print(f"✓ Content Parsed:")
        print(f"  Sections: {len(spec_parser)}")
        print(f"  Total length: {spec_parser.total_content_length}")


class ValidationCoordinator:
    """Coordinates validation of parsed data.
    
    Uses validator instances to check TOC and content quality,
    then returns validation results.
    """
    
    def __init__(self, validators: Dict, parsed_results: Dict):
        self.validators = validators
        self.parsed_results = parsed_results
        self.results = {}
    
    def validate_all(self):
        """Run all validators and collect results."""
        print("\n[STEP 4] Validating Results...")
        print("-" * 60)
        
        toc_valid = self._validate_toc()
        spec_valid = self._validate_spec()
        
        self.results = {
            "toc_valid": toc_valid,
            "spec_valid": spec_valid,
            "overall_valid": toc_valid and spec_valid
        }
    
    def _validate_toc(self) -> bool:
        """Run TOC validator and return result."""
        toc_validator = self.validators["toc"]
        toc_valid = toc_validator.validate(
            self.parsed_results["toc"]
        )
        
        self._print_validation_result("TOC", toc_valid, toc_validator)
        
        return toc_valid
    
    def _validate_spec(self) -> bool:
        """Run spec validator and return result."""
        spec_validator = self.validators["spec"]
        spec_valid = spec_validator.validate(
            self.parsed_results["spec"]
        )
        
        self._print_validation_result("Spec", spec_valid, spec_validator)
        
        return spec_valid
    
    def _print_validation_result(self, name: str, is_valid: bool, validator):
        """Print validation result for a validator."""
        status = '✓ PASS' if is_valid else '✗ FAIL'
        print(f"  {name} Validation: {status}")
        if not is_valid:
            print(f"    Errors: {validator.error_count}")


class OutputWriter:
    """Handles writing parsed results to files.
    
    Uses writer instances to save TOC entries, content sections,
    and validation reports to output files.
    """
    
    def __init__(self, writers: Dict, parsed_results: Dict):
        self.writers = writers
        self.parsed_results = parsed_results
    
    def write_all(self):
        """Write all output files."""
        print("\n[STEP 5] Writing Output Files...")
        print("-" * 60)
        
        self._write_toc()
        self._write_spec()
    
    def _write_toc(self):
        """Write TOC data to file."""
        toc_writer = self.writers["toc"]
        toc_success = toc_writer.write(self.parsed_results["toc"])
        self._print_write_result("TOC", toc_success, toc_writer)
    
    def _write_spec(self):
        """Write content data to file."""
        spec_writer = self.writers["spec"]
        spec_success = spec_writer.write(self.parsed_results["spec"])
        self._print_write_result("Spec", spec_success, spec_writer)
    
    def _print_write_result(self, name: str, success: bool, writer):
        """Print write result for a writer."""
        status = '✓ Written' if success else '✗ Failed'
        print(f"  {name}: {status}")
        print(f"    Lines: {writer.lines_written}")


class ReportGenerator:
    """Creates validation reports from parsing results.
    
    Combines parsing data, validation results, and execution stats
    into a comprehensive report dictionary.
    """
    
    def __init__(self, config: Dict):
        """Set up report generator with configuration data."""
        self.doc_title = config.get("doc_title")
        self.parsed_results = config.get("parsed_results")
        self.validation_results = config.get(
            "validation_results"
        )
        self.execution_stats = config.get("execution_stats")
        self.extractor = config.get("extractor")
    
    def generate(self) -> Dict:
        """Create and return the report data."""
        return {
            "document": self.doc_title,
            "validation_date": datetime.now().isoformat(),
            "summary": self._create_summary(),
            "validation_status": self._get_status(),
            "execution_stats": self.execution_stats
        }
    
    def _create_summary(self) -> Dict:
        """Build summary with counts and coverage."""
        return {
            "total_toc_sections": len(self.parsed_results["toc"]),
            "total_content_sections": len(
                self.parsed_results["spec"]
            ),
            "page_coverage": self._calculate_page_coverage()
        }
    
    def _calculate_page_coverage(self) -> Dict:
        """Calculate page coverage statistics."""
        missing = (
            self.extractor.total_pages -
            self.extractor.pages_processed
        )
        
        return {
            "total_pages": self.extractor.total_pages,
            "pages_covered": self.extractor.pages_processed,
            "pages_missing": missing,
            "coverage_percentage": round(
                self.extractor.get_coverage(),
                2
            )
        }
    
    def _get_status(self) -> str:
        """Return PASS or FAIL based on validation."""
        if self.validation_results["overall_valid"]:
            return "PASS"
        return "FAIL"


class USBPDParserOrchestrator:
    """Main coordinator for the USB PD parsing pipeline.
    
    Manages the complete process: component setup, PDF extraction,
    parsing, validation, output writing, and report generation.
    """
    
    def __init__(self, pdf_path: str, output_dir: str):
        """Set up orchestrator with PDF path and output directory."""
        self.__pdf_path = pdf_path
        self.__output_dir = output_dir
        self.__doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        
        self.__parsers = {}
        self.__writers = {}
        self.__validators = {}
        self.__parsed_results = {}
        self.__validation_results = {}
        self.__execution_stats = {}
        
        self._is_initialized = False
        self._extractor = None
    
    @property
    def pdf_path(self) -> str:
        """Get the PDF file path."""
    
    @property
    def output_dir(self) -> str:
        """Get the output directory path."""
    
    @property
    def is_initialized(self) -> bool:
        """Check if components have been initialized."""
    
    def initialize(self):
        """Set up all components and factories."""
        self._print_initialization_header()
        
        ComponentRegistrar.register_all()
        
        factory = ComponentFactory(
            self.__doc_title,
            self.__output_dir
        )
        
        self._create_components(factory)
        
        self._is_initialized = True
        self._print_initialization_complete()
    
    def _print_initialization_header(self):
        """Print initialization start message."""
        print("\n" + "="*60)
        print("INITIALIZING USB PD PARSER ORCHESTRATOR")
        print("="*60)
    
    def _create_components(self, factory: ComponentFactory):
        """Create all required components."""
        self._create_parsers(factory)
        self._create_writers(factory)
        self._create_validators(factory)
    
    def _create_parsers(self, factory: ComponentFactory):
        """Create parser components."""
        print("\n[1/3] Creating Parsers...")
        self.__parsers = factory.create_parsers()
        print("  ✓ Parsers created")
    
    def _create_writers(self, factory: ComponentFactory):
        """Create writer components."""
        print("\n[2/3] Creating Writers...")
        self.__writers = factory.create_writers()
        print("  ✓ Writers created")
    
    def _create_validators(self, factory: ComponentFactory):
        """Create validator components."""
        print("\n[3/3] Creating Validators...")
        self.__validators = factory.create_validators()
        print("  ✓ Validators created")
    
    def _print_initialization_complete(self):
        """Print initialization completion message."""
        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60 + "\n")
    
    def execute(self):
        """Run the complete parsing pipeline."""
        if not self._is_initialized:
            self.initialize()
        
        start_time = datetime.now()
        self._print_execution_start()
        
        text_data = self._extract_text()
        parsed_results = self._parse_data(text_data)
        validation_results = self._validate_data(parsed_results)
        self._write_outputs(parsed_results)
        
        execution_stats = self._finalize_execution(start_time)
        self._generate_report(parsed_results, validation_results, execution_stats)
        self._print_summary(parsed_results, execution_stats)
    
    def _print_execution_start(self):
        """Print execution start message."""
        print("\n" + "="*60)
        print("STARTING EXECUTION PIPELINE")
        print("="*60)
    
    def _extract_text(self) -> Dict[int, str]:
        """Extract text from PDF and return page mapping."""
        self._extractor = PDFExtractor(self.__pdf_path)
        return self._extractor.extract()
    
    def _parse_data(self, text_data: Dict[int, str]) -> Dict:
        """Parse TOC and content from text data."""
        parser_coord = ParsingCoordinator(
            self.__parsers,
            text_data
        )
        toc_data = parser_coord.parse_toc()
        spec_data = parser_coord.parse_content()
        return {"toc": toc_data, "spec": spec_data}
    
    def _validate_data(self, parsed_results: Dict) -> Dict:
        """Validate parsed results and return outcomes."""
        val_coord = ValidationCoordinator(
            self.__validators,
            parsed_results
        )
        val_coord.validate_all()
        return val_coord.results
    
    def _write_outputs(self, parsed_results: Dict):
        """Write parsed results to output files."""
        writer = OutputWriter(self.__writers, parsed_results)
        writer.write_all()
    
    def _finalize_execution(self, start_time: datetime) -> Dict:
        """Record execution timing and return stats."""
        duration = (datetime.now() - start_time).total_seconds()
        return {
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2)
        }
    
    def _generate_report(self, parsed_results: Dict, validation_results: Dict, execution_stats: Dict):
        """Create and write validation report."""
        print("\n[STEP 6] Generating Validation Report...")
        print("-" * 60)
        
        generator = ReportGenerator({
            "doc_title": self.__doc_title,
            "parsed_results": parsed_results,
            "validation_results": validation_results,
            "execution_stats": execution_stats,
            "extractor": self._extractor
        })
        
        report_data = generator.generate()
        
        report_writer = self.__writers["report"]
        success = report_writer.write(report_data)
        
        status = '✓ Generated' if success else '✗ Failed'
        print(f"  Report: {status}")
    
    def _print_summary(self, parsed_results: Dict, execution_stats: Dict):
        """Print final execution summary."""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        toc_count = len(parsed_results['toc'])
        spec_count = len(parsed_results['spec'])
        print(f"TOC Sections:      {toc_count:,}")
        print(f"Content Sections:  {spec_count:,}")
        print(f"Total Pages:       {self._extractor.total_pages:,}")
        print(
            f"Pages Covered:     "
            f"{self._extractor.pages_processed:,}"
        )
        print(f"Coverage:          {self._extractor.get_coverage():.1f}%")
        duration = execution_stats['duration_seconds']
        print(f"Duration:          {duration}s")
        print(f"\nOutput Directory:  {self.__output_dir}")
        print("="*60)
        print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
    
    def __str__(self) -> str:
        return (
            f"USBPDParserOrchestrator("
            f"initialized={self._is_initialized})"
        )
    
    def __enter__(self):
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    pdf_path = (
        project_root / "data" / "input" /
        "USB_PD_R3_2 V1.1 2024-10.pdf"
    )
    output_dir = project_root / "data" / "output"
    
    orchestrator = USBPDParserOrchestrator(
        str(pdf_path),
        str(output_dir)
    )
    orchestrator.execute()