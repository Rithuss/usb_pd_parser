"""
USB PD Parser Orchestrator
The crown jewel - demonstrates COMPOSITION PATTERN.

OOP Concepts:
- COMPOSITION: Has-a relationships
- DEPENDENCY INJECTION: Components passed in
- COORDINATION: Orchestrates multiple objects
- ENCAPSULATION: Private component management
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pdfplumber
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

# Import factories
from core.factories import ParserFactory, WriterFactory, ValidatorFactory

# Import concrete classes (for registration)
from parsers.usb_pd_toc_parser import USBPDTOCParser
from parsers.usb_pd_spec_parser import USBPDSpecParser
from writers.jsonl_writer import JSONLWriter
from writers.validation_report_writer import ValidationReportWriter
from strategies.toc_validation_strategy import TOCValidationStrategy
from strategies.spec_validation_strategy import SpecValidationStrategy


class USBPDParserOrchestrator:
    """
    Main orchestrator demonstrating COMPOSITION PATTERN.
    
    OOP Principles:
    - COMPOSITION: Contains multiple component objects
    - DEPENDENCY INJECTION: Components injected/created
    - COORDINATION: Manages workflow between components
    - ENCAPSULATION: Private component collections
    """
    
    def __init__(self, pdf_path: str, output_dir: str):
        """
        Initialize orchestrator with paths.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory path
        """
        # ENCAPSULATION: Private attributes
        self.__pdf_path = pdf_path
        self.__output_dir = output_dir
        self.__doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        
        # COMPOSITION: Collections of components
        self.__parsers = {}  # Parser objects
        self.__writers = {}  # Writer objects
        self.__validators = {}  # Validator objects
        
        # ENCAPSULATION: Private state
        self.__text_data = {}
        self.__parsed_results = {}
        self.__validation_results = {}
        self.__execution_stats = {}
        
        # ENCAPSULATION: Protected attributes
        self._is_initialized = False
        self._total_pages = 0
        self._pages_processed = 0
    
    # PROPERTY: Read-only access
    @property
    def pdf_path(self) -> str:
        """Get PDF path"""
        return self.__pdf_path
    
    @property
    def output_dir(self) -> str:
        """Get output directory"""
        return self.__output_dir
    
    @property
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._is_initialized
    
    @property
    def total_pages(self) -> int:
        """Get total pages processed"""
        return self._total_pages
    
    # PUBLIC METHOD: Initialize all components
    def initialize(self):
        """
        Initialize all components using FACTORY PATTERN.
        
        COMPOSITION: Creates and stores component objects.
        """
        print("\n" + "="*60)
        print("INITIALIZING USB PD PARSER ORCHESTRATOR")
        print("="*60)
        
        # Register all components first
        self.__register_components()
        
        # Create parsers using FACTORY PATTERN
        print("\n[1/3] Creating Parsers...")
        self.__parsers["toc"] = ParserFactory.create_parser(
            "toc",
            self.__doc_title
        )
        self.__parsers["spec"] = ParserFactory.create_parser(
            "spec",
            self.__doc_title
        )
        print("  ✓ TOC Parser created")
        print("  ✓ Spec Parser created")
        
        # Create writers using FACTORY PATTERN
        print("\n[2/3] Creating Writers...")
        toc_path = os.path.join(self.__output_dir, "usb_pd_toc.jsonl")
        spec_path = os.path.join(
            self.__output_dir,
            "usb_pd_spec.jsonl"
        )
        report_path = os.path.join(
            self.__output_dir,
            "validation_report.json"
        )
        
        self.__writers["toc"] = WriterFactory.create_writer(
            "jsonl",
            toc_path
        )
        self.__writers["spec"] = WriterFactory.create_writer(
            "jsonl",
            spec_path
        )
        self.__writers["report"] = WriterFactory.create_writer(
            "validation",
            report_path
        )
        print("  ✓ JSONL Writers created")
        print("  ✓ Validation Report Writer created")
        
        # Create validators using FACTORY PATTERN
        print("\n[3/3] Creating Validators...")
        self.__validators["toc"] = ValidatorFactory.create_validator(
            "toc"
        )
        self.__validators["spec"] = ValidatorFactory.create_validator(
            "spec"
        )
        print("  ✓ TOC Validator created")
        print("  ✓ Spec Validator created")
        
        self._is_initialized = True
        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60 + "\n")
    
    # PROTECTED METHOD: Register components with factories
    def _register_components(self):
        """Register all components with factories"""
        self.__register_components()
    
    # ENCAPSULATION: Private registration
    def __register_components(self):
        """
        Register components with factories (FACTORY PATTERN).
        """
        # Parsers
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)
        
        # Writers
        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer(
            "validation",
            ValidationReportWriter
        )
        
        # Validators
        ValidatorFactory.register_validator(
            "toc",
            TOCValidationStrategy
        )
        ValidatorFactory.register_validator(
            "spec",
            SpecValidationStrategy
        )
    
    # PUBLIC METHOD: Execute full pipeline
    def execute(self):
        """
        Execute complete parsing pipeline.
        
        COORDINATION: Orchestrates all components.
        """
        if not self._is_initialized:
            self.initialize()
        
        start_time = datetime.now()
        
        print("\n" + "="*60)
        print("STARTING EXECUTION PIPELINE")
        print("="*60)
        
        # Step 1: Extract PDF text
        self.__extract_pdf_text()
        
        # Step 2: Parse TOC
        self.__parse_toc()
        
        # Step 3: Parse content
        self.__parse_content()
        
        # Step 4: Validate results
        self.__validate_results()
        
        # Step 5: Write outputs
        self.__write_outputs()
        
        # Step 6: Generate report
        self.__generate_report()
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.__execution_stats = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": round(duration, 2)
        }
        
        # Print summary
        self.__print_summary()
    
    # ENCAPSULATION: Private pipeline steps
    def __extract_pdf_text(self):
        """Extract text from PDF"""
        print("\n[STEP 1] Extracting PDF Text...")
        print("-" * 60)
        
        with pdfplumber.open(self.__pdf_path) as pdf:
            self._total_pages = len(pdf.pages)
            print(f"Total pages: {self._total_pages}")
            
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    self.__text_data[i] = text
                    self._pages_processed += 1
                else:
                    self.__text_data[i] = ""
                
                if i % 100 == 0:
                    print(f"  Processed: {i}/{self._total_pages}")
        
        coverage = (
            self._pages_processed / self._total_pages * 100
        )
        print(f"\n✓ Extraction Complete:")
        print(f"  Pages processed: {self._pages_processed}")
        print(f"  Coverage: {coverage:.1f}%")
    
    def __parse_toc(self):
        """Parse Table of Contents"""
        print("\n[STEP 2] Parsing Table of Contents...")
        print("-" * 60)
        
        toc_parser = self.__parsers["toc"]
        toc_data = toc_parser.parse(self.__text_data)
        
        self.__parsed_results["toc"] = toc_data
        
        print(f"✓ TOC Parsed:")
        print(f"  Sections: {len(toc_parser)}")
        print(f"  Max depth: {toc_parser.max_depth}")
    
    def __parse_content(self):
        """Parse specification content"""
        print("\n[STEP 3] Parsing Specification Content...")
        print("-" * 60)
        
        spec_parser = self.__parsers["spec"]
        spec_data = spec_parser.parse(self.__text_data)
        
        self.__parsed_results["spec"] = spec_data
        
        print(f"✓ Content Parsed:")
        print(f"  Sections: {len(spec_parser)}")
        print(f"  Total length: {spec_parser.total_content_length}")
    
    def __validate_results(self):
        """Validate parsed results"""
        print("\n[STEP 4] Validating Results...")
        print("-" * 60)
        
        # Validate TOC
        toc_validator = self.__validators["toc"]
        toc_valid = toc_validator.validate(
            self.__parsed_results["toc"]
        )
        
        print(f"  TOC Validation: {'✓ PASS' if toc_valid else '✗ FAIL'}")
        if not toc_valid:
            print(f"    Errors: {toc_validator.error_count}")
        
        # Validate Spec
        spec_validator = self.__validators["spec"]
        spec_valid = spec_validator.validate(
            self.__parsed_results["spec"]
        )
        
        print(f"  Spec Validation: {'✓ PASS' if spec_valid else '✗ FAIL'}")
        if not spec_valid:
            print(f"    Errors: {spec_validator.error_count}")
        
        self.__validation_results = {
            "toc_valid": toc_valid,
            "spec_valid": spec_valid,
            "overall_valid": toc_valid and spec_valid
        }
    
    def __write_outputs(self):
        """Write output files"""
        print("\n[STEP 5] Writing Output Files...")
        print("-" * 60)
        
        # Write TOC
        toc_writer = self.__writers["toc"]
        toc_success = toc_writer.write(self.__parsed_results["toc"])
        print(f"  TOC: {'✓ Written' if toc_success else '✗ Failed'}")
        print(f"    Lines: {toc_writer.lines_written}")
        
        # Write Spec
        spec_writer = self.__writers["spec"]
        spec_success = spec_writer.write(
            self.__parsed_results["spec"]
        )
        print(f"  Spec: {'✓ Written' if spec_success else '✗ Failed'}")
        print(f"    Lines: {spec_writer.lines_written}")
    
    def __generate_report(self):
        """Generate validation report"""
        print("\n[STEP 6] Generating Validation Report...")
        print("-" * 60)
        
        report_data = {
            "document": self.__doc_title,
            "validation_date": datetime.now().isoformat(),
            "summary": {
                "total_toc_sections": len(
                    self.__parsed_results["toc"]
                ),
                "total_content_sections": len(
                    self.__parsed_results["spec"]
                ),
                "page_coverage": {
                    "total_pages": self._total_pages,
                    "pages_covered": self._pages_processed,
                    "pages_missing": (
                        self._total_pages - self._pages_processed
                    ),
                    "coverage_percentage": round(
                        self._pages_processed / self._total_pages * 100,
                        2
                    )
                }
            },
            "validation_status": (
                "PASS" if self.__validation_results["overall_valid"]
                else "FAIL"
            ),
            "execution_stats": self.__execution_stats
        }
        
        report_writer = self.__writers["report"]
        success = report_writer.write(report_data)
        
        print(f"  Report: {'✓ Generated' if success else '✗ Failed'}")
    
    def __print_summary(self):
        """Print execution summary"""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"TOC Sections:      "
              f"{len(self.__parsed_results['toc']):,}")
        print(f"Content Sections:  "
              f"{len(self.__parsed_results['spec']):,}")
        print(f"Total Pages:       {self._total_pages:,}")
        print(f"Pages Covered:     {self._pages_processed:,}")
        print(f"Coverage:          "
              f"{self._pages_processed/self._total_pages*100:.1f}%")
        print(f"Duration:          "
              f"{self.__execution_stats['duration_seconds']}s")
        print(f"\nOutput Directory:  {self.__output_dir}")
        print("="*60)
        print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable representation"""
        return (
            f"USBPDParserOrchestrator("
            f"pages={self._total_pages}, "
            f"initialized={self._is_initialized})"
        )
    
    # SPECIAL METHOD: Length (total pages)
    def __len__(self) -> int:
        """Return total pages"""
        return self._total_pages
    
    # SPECIAL METHOD: Context manager
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Cleanup if needed
        pass


# Entry point for direct execution
if __name__ == "__main__":
    # Get paths
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "input" / "USB_PD_R3_2 V1.1 2024-10.pdf"
    output_dir = project_root / "data" / "output"
    
    # Create and execute orchestrator
    orchestrator = USBPDParserOrchestrator(
        str(pdf_path),
        str(output_dir)
    )
    orchestrator.execute()