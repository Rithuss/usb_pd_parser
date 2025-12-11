"""
USB PD Parser Orchestrator - REFACTORED
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pdfplumber
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from core.factories import ParserFactory, WriterFactory, ValidatorFactory
from parsers.usb_pd_toc_parser import USBPDTOCParser
from parsers.usb_pd_spec_parser import USBPDSpecParser
from writers.jsonl_writer import JSONLWriter
from writers.validation_report_writer import ValidationReportWriter
from strategies.toc_validation_strategy import TOCValidationStrategy
from strategies.spec_validation_strategy import SpecValidationStrategy


class ProgressTracker:
    
    def __init__(self):
        self.steps_total = 7
        self.steps_completed = 0
        self.current_step = ""
        
    def start_step(self, step_name: str):
        self.steps_completed += 1
        self.current_step = step_name
        print(f"\n[STEP {self.steps_completed}/{self.steps_total}] {step_name}...")
        print("-" * 60)
    
    def complete_step(self, message: str = ""):
        if message:
            print(f"✓ {message}")


class StatisticsCollector:
    
    def __init__(self):
        self.stats = {
            "extraction": {},
            "parsing": {},
            "validation": {},
            "output": {}
        }
    
    def add_extraction_stats(self, total_pages: int, pages_processed: int):
        self.stats["extraction"] = {
            "total_pages": total_pages,
            "pages_processed": pages_processed,
            "coverage_pct": round(pages_processed / total_pages * 100, 2)
        }
    
    def add_parsing_stats(self, toc_count: int, spec_count: int):
        self.stats["parsing"] = {
            "toc_sections": toc_count,
            "spec_sections": spec_count
        }
    
    def add_validation_stats(self, toc_valid: bool, spec_valid: bool):
        self.stats["validation"] = {
            "toc_valid": toc_valid,
            "spec_valid": spec_valid,
            "overall_valid": toc_valid and spec_valid
        }
    
    def add_output_stats(self, files_written: List[str]):
        self.stats["output"] = {
            "files_written": files_written,
            "file_count": len(files_written)
        }
    
    def get_all_stats(self) -> Dict:
        return self.stats.copy()


class ComponentRegistry:
    
    @staticmethod
    def register_all():
        ParserFactory.register_parser("toc", USBPDTOCParser)
        ParserFactory.register_parser("spec", USBPDSpecParser)
        WriterFactory.register_writer("jsonl", JSONLWriter)
        WriterFactory.register_writer("validation", ValidationReportWriter)
        ValidatorFactory.register_validator("toc", TOCValidationStrategy)
        ValidatorFactory.register_validator("spec", SpecValidationStrategy)


class PDFTextExtractor:
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0
        self.pages_processed = 0
    
    def extract(self) -> Dict[int, str]:
        text_data = {}
        
        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)
            print(f"Total pages: {self.total_pages}")
            
            text_data = self._extract_pages(pdf)
        
        coverage = (self.pages_processed / self.total_pages * 100)
        print(f"\n✓ Extraction Complete:")
        print(f"  Pages processed: {self.pages_processed}")
        print(f"  Coverage: {coverage:.1f}%")
        
        return text_data
    
    def _extract_pages(self, pdf) -> Dict[int, str]:
        text_data = {}
        
        for i, page in enumerate(pdf.pages, start=1):
            text = self._extract_page_text(page)
            text_data[i] = text
            
            if text:
                self.pages_processed += 1
            
            if i % 100 == 0:
                print(f"  Processed: {i}/{self.total_pages}")
        
        return text_data
    
    def _extract_page_text(self, page) -> str:
        text = page.extract_text()
        return text if text else ""


class USBPDParserOrchestrator:
    
    def __init__(self, pdf_path: str, output_dir: str):
        self.__pdf_path = pdf_path
        self.__output_dir = output_dir
        self.__doc_title = "USB Power Delivery Specification, Revision 3.2, Version 1.1, 2024-10"
        
        self.__parsers = {}
        self.__writers = {}
        self.__validators = {}
        self.__text_data = {}
        self.__parsed_results = {}
        
        self.__progress = ProgressTracker()
        self.__statistics = StatisticsCollector()
        
        self._is_initialized = False
        self._total_pages = 0
        self._pages_processed = 0
        self.__start_time = None
        self.__end_time = None
    
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
        print("\n" + "="*60)
        print("INITIALIZING USB PD PARSER ORCHESTRATOR")
        print("="*60)
        
        ComponentRegistry.register_all()
        self._create_parsers()
        self._create_writers()
        self._create_validators()
        
        self._is_initialized = True
        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60 + "\n")
    
    def _create_parsers(self):
        print("\n[1/3] Creating Parsers...")
        self.__parsers["toc"] = ParserFactory.create_parser("toc", self.__doc_title)
        self.__parsers["spec"] = ParserFactory.create_parser("spec", self.__doc_title)
        print("  ✓ TOC Parser created")
        print("  ✓ Spec Parser created")
    
    def _create_writers(self):
        print("\n[2/3] Creating Writers...")
        
        paths = self._get_output_paths()
        
        self.__writers["toc"] = WriterFactory.create_writer("jsonl", paths["toc"])
        self.__writers["spec"] = WriterFactory.create_writer("jsonl", paths["spec"])
        self.__writers["report"] = WriterFactory.create_writer("validation", paths["report"])
        self.__writers["summary"] = WriterFactory.create_writer("validation", paths["summary"])
        
        print("  ✓ JSONL Writers created")
        print("  ✓ Report Writers created")
    
    def _create_validators(self):
        print("\n[3/3] Creating Validators...")
        self.__validators["toc"] = ValidatorFactory.create_validator("toc")
        self.__validators["spec"] = ValidatorFactory.create_validator("spec")
        print("  ✓ Validators created")
    
    def _get_output_paths(self) -> Dict[str, str]:
        return {
            "toc": os.path.join(self.__output_dir, "usb_pd_toc.jsonl"),
            "spec": os.path.join(self.__output_dir, "usb_pd_spec.jsonl"),
            "report": os.path.join(self.__output_dir, "validation_report.json"),
            "summary": os.path.join(self.__output_dir, "execution_summary.json")
        }
    
    def execute(self):
        if not self._is_initialized:
            self.initialize()
        
        self.__start_time = datetime.now()
        
        print("\n" + "="*60)
        print("STARTING EXECUTION PIPELINE")
        print("="*60)
        
        self._execute_extraction()
        self._execute_toc_parsing()
        self._execute_spec_parsing()
        self._execute_validation()
        self._execute_writing()
        self._execute_report_generation()
        self._execute_summary_generation()
        
        self.__end_time = datetime.now()
        self._print_final_summary()
    
    def _execute_extraction(self):
        self.__progress.start_step("Extracting PDF Text")
        
        extractor = PDFTextExtractor(self.__pdf_path)
        self.__text_data = extractor.extract()
        
        self._total_pages = extractor.total_pages
        self._pages_processed = extractor.pages_processed
        
        self.__statistics.add_extraction_stats(self._total_pages, self._pages_processed)
        
        self.__progress.complete_step("Text extraction complete")
    
    def _execute_toc_parsing(self):
        self.__progress.start_step("Parsing Table of Contents")
        
        toc_parser = self.__parsers["toc"]
        toc_data = toc_parser.parse(self.__text_data)
        self.__parsed_results["toc"] = toc_data
        
        print(f"✓ TOC Parsed: {len(toc_parser)} sections")
        print(f"  Max depth: {toc_parser.max_depth}")
    
    def _execute_spec_parsing(self):
        self.__progress.start_step("Parsing Specification Content")
        
        spec_parser = self.__parsers["spec"]
        spec_data = spec_parser.parse(self.__text_data)
        self.__parsed_results["spec"] = spec_data
        
        self.__statistics.add_parsing_stats(
            len(self.__parsed_results["toc"]),
            len(self.__parsed_results["spec"])
        )
        
        print(f"✓ Content Parsed: {len(spec_parser)} sections")
    
    def _execute_validation(self):
        self.__progress.start_step("Validating Results")
        
        toc_valid = self._validate_toc()
        spec_valid = self._validate_spec()
        
        self.__statistics.add_validation_stats(toc_valid, spec_valid)
        
        print(f"✓ Validation complete")
    
    def _validate_toc(self) -> bool:
        validator = self.__validators["toc"]
        valid = validator.validate(self.__parsed_results["toc"])
        
        status = '✓ PASS' if valid else '✗ FAIL'
        print(f"  TOC Validation: {status}")
        
        return valid
    
    def _validate_spec(self) -> bool:
        validator = self.__validators["spec"]
        valid = validator.validate(self.__parsed_results["spec"])
        
        status = '✓ PASS' if valid else '✗ FAIL'
        print(f"  Spec Validation: {status}")
        
        return valid
    
    def _execute_writing(self):
        self.__progress.start_step("Writing Output Files")
        
        files_written = []
        
        if self._write_toc():
            files_written.append("usb_pd_toc.jsonl")
        
        if self._write_spec():
            files_written.append("usb_pd_spec.jsonl")
        
        self.__statistics.add_output_stats(files_written)
    
    def _write_toc(self) -> bool:
        writer = self.__writers["toc"]
        success = writer.write(self.__parsed_results["toc"])
        
        status = '✓ Written' if success else '✗ Failed'
        print(f"  TOC: {status} ({writer.lines_written} lines)")
        
        return success
    
    def _write_spec(self) -> bool:
        writer = self.__writers["spec"]
        success = writer.write(self.__parsed_results["spec"])
        
        status = '✓ Written' if success else '✗ Failed'
        print(f"  Spec: {status} ({writer.lines_written} lines)")
        
        return success
    
    def _execute_report_generation(self):
        self.__progress.start_step("Generating Validation Report")
        
        report_data = self._build_validation_report()
        writer = self.__writers["report"]
        success = writer.write(report_data)
        
        status = '✓ Generated' if success else '✗ Failed'
        print(f"  Report: {status}")
    
    def _execute_summary_generation(self):
        self.__progress.start_step("Generating Execution Summary")
        
        summary_data = self._build_execution_summary()
        writer = self.__writers["summary"]
        success = writer.write(summary_data)
        
        status = '✓ Generated' if success else '✗ Failed'
        print(f"  Summary: {status}")
    
    def _build_validation_report(self) -> Dict:
        return {
            "document": self.__doc_title,
            "validation_date": datetime.now().isoformat(),
            "summary": {
                "total_toc_sections": len(self.__parsed_results["toc"]),
                "total_content_sections": len(self.__parsed_results["spec"]),
                "page_coverage": {
                    "total_pages": self._total_pages,
                    "pages_covered": self._pages_processed,
                    "pages_missing": self._total_pages - self._pages_processed,
                    "coverage_percentage": round(self._pages_processed / self._total_pages * 100, 2)
                }
            },
            "validation_status": "PASS" if self.__statistics.stats["validation"]["overall_valid"] else "FAIL"
        }
    
    def _build_execution_summary(self) -> Dict:
        if self.__end_time is None:
            self.__end_time = datetime.now()
    
        duration = (self.__end_time - self.__start_time).total_seconds()
    
        return {
            "execution_metadata": {
                "start_time": self.__start_time.isoformat(),
                "end_time": self.__end_time.isoformat(),
                "duration_seconds": round(duration, 2)
            },
            "statistics": self.__statistics.get_all_stats(),
            "output_files": list(self._get_output_paths().values())
        }
    
    def _print_final_summary(self):
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        
        stats = self.__statistics.get_all_stats()
        
        print(f"TOC Sections:      {stats['parsing']['toc_sections']:,}")
        print(f"Content Sections:  {stats['parsing']['spec_sections']:,}")
        print(f"Total Pages:       {stats['extraction']['total_pages']:,}")
        print(f"Pages Covered:     {stats['extraction']['pages_processed']:,}")
        print(f"Coverage:          {stats['extraction']['coverage_pct']:.1f}%")
        
        duration = (self.__end_time - self.__start_time).total_seconds()
        print(f"Duration:          {duration:.2f}s")
        
        print(f"\nOutput Directory:  {self.__output_dir}")
        print(f"Files Generated:   {stats['output']['file_count']}")
        print("="*60)
        print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
    
    def __str__(self) -> str:
        return f"USBPDParserOrchestrator(pages={self._total_pages}, initialized={self._is_initialized})"
    
    def __len__(self) -> int:
        return self._total_pages


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "input" / "USB_PD_R3_2 V1.1 2024-10.pdf"
    output_dir = project_root / "data" / "output"
    
    orchestrator = USBPDParserOrchestrator(str(pdf_path), str(output_dir))
    orchestrator.execute()