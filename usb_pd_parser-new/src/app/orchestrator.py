"""
USB PD Parser Orchestrator
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
    """Handles component registration with factories."""
    
    @staticmethod
    def register_all():
        """Register all components."""
        ComponentRegistrar._register_parsers()
        ComponentRegistrar._register_writers()
        ComponentRegistrar._register_validators()
    
    @staticmethod
    def _register_parsers():
        """Register parsers."""
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)
    
    @staticmethod
    def _register_writers():
        """Register writers."""
        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer(
            "validation",
            ValidationReportWriter
        )
    
    @staticmethod
    def _register_validators():
        """Register validators."""
        ValidatorFactory.register_validator(
            "toc",
            TOCValidationStrategy
        )
        ValidatorFactory.register_validator(
            "spec",
            SpecValidationStrategy
        )


class ComponentFactory:
    """Factory for creating all components."""
    
    def __init__(self, doc_title: str, output_dir: str):
        self.doc_title = doc_title
        self.output_dir = output_dir
    
    def create_parsers(self) -> Dict:
        """Create parser components."""
        return {
            "toc": ParserFactory.create_parser("toc", self.doc_title),
            "spec": ParserFactory.create_parser("spec", self.doc_title)
        }
    
    def create_writers(self) -> Dict:
        """Create writer components."""
        return {
            "toc": WriterFactory.create_writer(
                "jsonl",
                os.path.join(self.output_dir, "usb_pd_toc.jsonl")
            ),
            "spec": WriterFactory.create_writer(
                "jsonl",
                os.path.join(self.output_dir, "usb_pd_spec.jsonl")
            ),
            "report": WriterFactory.create_writer(
                "validation",
                os.path.join(
                    self.output_dir,
                    "validation_report.json"
                )
            )
        }
    
    def create_validators(self) -> Dict:
        """Create validator components."""
        return {
            "toc": ValidatorFactory.create_validator("toc"),
            "spec": ValidatorFactory.create_validator("spec")
        }


class PDFExtractor:
    """Handles PDF text extraction."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0
        self.pages_processed = 0
    
    def extract(self) -> Dict[int, str]:
        """Extract text from PDF."""
        print("\n[STEP 1] Extracting PDF Text...")
        print("-" * 60)
        
        text_data = {}
        
        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)
            print(f"Total pages: {self.total_pages}")
            
            text_data = self._process_pages(pdf.pages)
        
        self._print_summary()
        return text_data
    
    def _process_pages(self, pages) -> Dict[int, str]:
        """Process all pages."""
        text_data = {}
        
        for i, page in enumerate(pages, start=1):
            text = page.extract_text()
            text_data[i] = text if text else ""
            
            if text:
                self.pages_processed += 1
            
            if i % 100 == 0:
                print(f"  Processed: {i}/{self.total_pages}")
        
        return text_data
    
    def _print_summary(self):
        """Print extraction summary."""
        coverage = (self.pages_processed / self.total_pages * 100)
        print(f"\n✓ Extraction Complete:")
        print(f"  Pages processed: {self.pages_processed}")
        print(f"  Coverage: {coverage:.1f}%")
    
    def get_coverage(self) -> float:
        """Get coverage percentage."""
        if self.total_pages > 0:
            return (self.pages_processed / self.total_pages * 100)
        return 0


class ParsingCoordinator:
    """Coordinates parsing operations."""
    
    def __init__(self, parsers: Dict, text_data: Dict[int, str]):
        self.parsers = parsers
        self.text_data = text_data
        self.results = {}
    
    def parse_toc(self) -> List[Dict]:
        """Parse Table of Contents."""
        print("\n[STEP 2] Parsing Table of Contents...")
        print("-" * 60)
        
        toc_parser = self.parsers["toc"]
        toc_data = toc_parser.parse(self.text_data)
        self.results["toc"] = toc_data
        
        print(f"✓ TOC Parsed:")
        print(f"  Sections: {len(toc_parser)}")
        print(f"  Max depth: {toc_parser.max_depth}")
        
        return toc_data
    
    def parse_content(self) -> List[Dict]:
        """Parse specification content."""
        print("\n[STEP 3] Parsing Specification Content...")
        print("-" * 60)
        
        spec_parser = self.parsers["spec"]
        spec_data = spec_parser.parse(self.text_data)
        self.results["spec"] = spec_data
        
        print(f"✓ Content Parsed:")
        print(f"  Sections: {len(spec_parser)}")
        print(f"  Total length: {spec_parser.total_content_length}")
        
        return spec_data


class ValidationCoordinator:
    """Coordinates validation operations."""
    
    def __init__(self, validators: Dict, parsed_results: Dict):
        self.validators = validators
        self.parsed_results = parsed_results
        self.results = {}
    
    def validate_all(self):
        """Validate all parsed results."""
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
        """Validate TOC."""
        toc_validator = self.validators["toc"]
        toc_valid = toc_validator.validate(
            self.parsed_results["toc"]
        )
        
        status = '✓ PASS' if toc_valid else '✗ FAIL'
        print(f"  TOC Validation: {status}")
        if not toc_valid:
            print(f"    Errors: {toc_validator.error_count}")
        
        return toc_valid
    
    def _validate_spec(self) -> bool:
        """Validate spec."""
        spec_validator = self.validators["spec"]
        spec_valid = spec_validator.validate(
            self.parsed_results["spec"]
        )
        
        status = '✓ PASS' if spec_valid else '✗ FAIL'
        print(f"  Spec Validation: {status}")
        if not spec_valid:
            print(f"    Errors: {spec_validator.error_count}")
        
        return spec_valid


class OutputWriter:
    """Handles writing output files."""
    
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
        """Write TOC file."""
        toc_writer = self.writers["toc"]
        toc_success = toc_writer.write(self.parsed_results["toc"])
        status = '✓ Written' if toc_success else '✗ Failed'
        print(f"  TOC: {status}")
        print(f"    Lines: {toc_writer.lines_written}")
    
    def _write_spec(self):
        """Write spec file."""
        spec_writer = self.writers["spec"]
        spec_success = spec_writer.write(self.parsed_results["spec"])
        status = '✓ Written' if spec_success else '✗ Failed'
        print(f"  Spec: {status}")
        print(f"    Lines: {spec_writer.lines_written}")


class ReportGenerator:
    """Generates validation report."""
    
    def __init__(
        self,
        doc_title: str,
        parsed_results: Dict,
        validation_results: Dict,
        execution_stats: Dict,
        extractor: PDFExtractor
    ):
        self.doc_title = doc_title
        self.parsed_results = parsed_results
        self.validation_results = validation_results
        self.execution_stats = execution_stats
        self.extractor = extractor
    
    def generate(self) -> Dict:
        """Generate report data."""
        return {
            "document": self.doc_title,
            "validation_date": datetime.now().isoformat(),
            "summary": self._create_summary(),
            "validation_status": self._get_status(),
            "execution_stats": self.execution_stats
        }
    
    def _create_summary(self) -> Dict:
        """Create summary."""
        missing = (
            self.extractor.total_pages -
            self.extractor.pages_processed
        )
        
        return {
            "total_toc_sections": len(self.parsed_results["toc"]),
            "total_content_sections": len(
                self.parsed_results["spec"]
            ),
            "page_coverage": {
                "total_pages": self.extractor.total_pages,
                "pages_covered": self.extractor.pages_processed,
                "pages_missing": missing,
                "coverage_percentage": round(
                    self.extractor.get_coverage(),
                    2
                )
            }
        }
    
    def _get_status(self) -> str:
        """Get validation status."""
        if self.validation_results["overall_valid"]:
            return "PASS"
        return "FAIL"


class USBPDParserOrchestrator:
    """Main orchestrator with reduced complexity."""
    
    def __init__(self, pdf_path: str, output_dir: str):
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
        return self.__pdf_path
    
    @property
    def output_dir(self) -> str:
        return self.__output_dir
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized
    
    def initialize(self):
        """Initialize all components."""
        print("\n" + "="*60)
        print("INITIALIZING USB PD PARSER ORCHESTRATOR")
        print("="*60)
        
        ComponentRegistrar.register_all()
        
        factory = ComponentFactory(
            self.__doc_title,
            self.__output_dir
        )
        
        print("\n[1/3] Creating Parsers...")
        self.__parsers = factory.create_parsers()
        print("  ✓ Parsers created")
        
        print("\n[2/3] Creating Writers...")
        self.__writers = factory.create_writers()
        print("  ✓ Writers created")
        
        print("\n[3/3] Creating Validators...")
        self.__validators = factory.create_validators()
        print("  ✓ Validators created")
        
        self._is_initialized = True
        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60 + "\n")
    
    def execute(self):
        """Execute complete parsing pipeline."""
        if not self._is_initialized:
            self.initialize()
        
        start_time = datetime.now()
        self._print_execution_start()
        
        text_data = self._extract_text()
        self._parse_data(text_data)
        self._validate_data()
        self._write_outputs()
        
        self._finalize_execution(start_time)
        self._generate_report()
        self._print_summary()
    
    def _print_execution_start(self):
        """Print execution start header."""
        print("\n" + "="*60)
        print("STARTING EXECUTION PIPELINE")
        print("="*60)
    
    def _extract_text(self) -> Dict[int, str]:
        """Extract text from PDF."""
        self._extractor = PDFExtractor(self.__pdf_path)
        return self._extractor.extract()
    
    def _parse_data(self, text_data: Dict[int, str]):
        """Parse TOC and content data."""
        parser_coord = ParsingCoordinator(
            self.__parsers,
            text_data
        )
        parser_coord.parse_toc()
        parser_coord.parse_content()
        self.__parsed_results = parser_coord.results
    
    def _validate_data(self):
        """Validate parsed results."""
        val_coord = ValidationCoordinator(
            self.__validators,
            self.__parsed_results
        )
        val_coord.validate_all()
        self.__validation_results = val_coord.results
    
    def _write_outputs(self):
        """Write output files."""
        writer = OutputWriter(self.__writers, self.__parsed_results)
        writer.write_all()
    
    def _finalize_execution(self, start_time: datetime):
        """Finalize execution with timing."""
        duration = (datetime.now() - start_time).total_seconds()
        self.__execution_stats = {
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2)
        }
    
    def _generate_report(self):
        """Generate validation report."""
        print("\n[STEP 6] Generating Validation Report...")
        print("-" * 60)
        
        generator = ReportGenerator(
            self.__doc_title,
            self.__parsed_results,
            self.__validation_results,
            self.__execution_stats,
            self._extractor
        )
        
        report_data = generator.generate()
        
        report_writer = self.__writers["report"]
        success = report_writer.write(report_data)
        
        status = '✓ Generated' if success else '✗ Failed'
        print(f"  Report: {status}")
    
    def _print_summary(self):
        """Print execution summary."""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        toc_count = len(self.__parsed_results['toc'])
        spec_count = len(self.__parsed_results['spec'])
        print(f"TOC Sections:      {toc_count:,}")
        print(f"Content Sections:  {spec_count:,}")
        print(f"Total Pages:       {self._extractor.total_pages:,}")
        print(
            f"Pages Covered:     "
            f"{self._extractor.pages_processed:,}"
        )
        print(f"Coverage:          {self._extractor.get_coverage():.1f}%")
        duration = self.__execution_stats['duration_seconds']
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