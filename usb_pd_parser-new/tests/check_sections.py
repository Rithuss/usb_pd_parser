"""
Enhanced Section Validation Script 
"""
import json
import os
from typing import Dict, List, Tuple


class FileChecker:
    """Handles file existence checking."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.toc_file = os.path.join(
            output_dir,
            "usb_pd_toc.jsonl"
        )
        self.spec_file = os.path.join(
            output_dir,
            "usb_pd_spec.jsonl"
        )
        self.validation_file = os.path.join(
            output_dir,
            "validation_report.json"
        )
    
    def check_files(self) -> Dict[str, bool]:
        """Check existence of all required files."""
        return {
            "TOC": os.path.exists(self.toc_file),
            "Spec": os.path.exists(self.spec_file),
            "Validation": os.path.exists(self.validation_file)
        }
    
    def all_required_exist(self) -> bool:
        """Check if all required files exist."""
        files = self.check_files()
        return files["TOC"] and files["Spec"]


class DataAnalyzer:
    """Analyzes extracted data from JSONL files."""
    
    def __init__(self, toc_file: str, spec_file: str):
        self.toc_file = toc_file
        self.spec_file = spec_file
    
    def analyze_toc(self) -> Tuple[int, List[Dict]]:
        """Analyze TOC file by processing entries."""
        return self._process_toc_file()
    
    def _process_toc_file(self) -> Tuple[int, List[Dict]]:
        """Process TOC file and collect count and samples."""
        count = 0
        samples = []
        
        with open(self.toc_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    count += 1
                    if i < 3:
                        samples.append(json.loads(line))
        
        return count, samples
    
    def analyze_spec(self) -> Tuple[int, List[Dict], Dict[str, float]]:
        """Analyze spec file by processing entries and computing metrics."""
        count, samples, total_length, non_empty = self._process_spec_file()
        metrics = self._compute_spec_metrics(count, total_length, non_empty)
        return count, samples, metrics
    
    def _process_spec_file(self) -> Tuple[int, List[Dict], int, int]:
        """Process spec file and collect raw statistics."""
        count = 0
        samples = []
        total_length = 0
        non_empty = 0
        
        with open(self.spec_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    count += 1
                    entry = json.loads(line)
                    content = entry.get("content", "")
                    total_length += len(content)
                    
                    if content.strip():
                        non_empty += 1
                    
                    if i < 3:
                        samples.append(entry)
        
        return count, samples, total_length, non_empty
    
    def _compute_spec_metrics(
        self,
        count: int,
        total_length: int,
        non_empty: int
    ) -> Dict[str, float]:
        """Compute metrics from raw statistics."""
        avg_length = total_length / count if count > 0 else 0
        quality_pct = non_empty / count * 100 if count > 0 else 0
        
        return {
            "avg_content_length": avg_length,
            "content_quality_pct": quality_pct,
            "non_empty_count": non_empty
        }


class ValidationAnalyzer:
    """Analyzes validation report."""
    
    def __init__(self, validation_file: str):
        self.validation_file = validation_file
        self.data = None
    
    def load_data(self) -> bool:
        """Load validation data."""
        if not os.path.exists(self.validation_file):
            return False
        
        with open(self.validation_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        return True
    
    def get_page_coverage(self) -> Dict:
        """Get page coverage information."""
        if not self.data:
            return {}
        
        summary = self.data.get("summary", {})
        return summary.get("page_coverage", {})
    
    def get_content_analysis(self) -> Dict:
        """Get content analysis."""
        if not self.data:
            return {}
        
        return self.data.get("content_analysis", {})
    
    def get_toc_analysis(self) -> Dict:
        """Get TOC analysis."""
        if not self.data:
            return {}
        
        return self.data.get("toc_analysis", {})
    
    def get_metrics(self) -> Dict:
        """Get detailed metrics."""
        if not self.data:
            return {}
        
        return self.data.get("detailed_metrics", {})
    
    def get_status(self) -> str:
        """Get validation status."""
        if not self.data:
            return "UNKNOWN"
        
        return self.data.get("validation_status", "UNKNOWN")


class ReportPrinter:
    """Handles printing of validation report."""
    
    @staticmethod
    def print_header():
        """Print report header."""
        print("="*70)
        print("USB PD PARSER - VALIDATION REPORT")
        print("="*70)
    
    @staticmethod
    def print_file_status(files_status: Dict[str, bool]):
        """Print file status."""
        print("\n📊 FILE STATUS:")
        for name, exists in files_status.items():
            status = "✓ Found" if exists else "✗ Missing"
            print(f"  {status:12} - {name}")
    
    @staticmethod
    def print_extraction_stats(toc_count: int, spec_count: int):
        """Print extraction statistics."""
        print("\n📈 EXTRACTION STATISTICS:")
        print(f"  TOC Sections:        {toc_count:,}")
        print(f"  Content Sections:    {spec_count:,}")
        match = '✓ Yes' if toc_count == spec_count else '✗ No'
        print(f"  Sections Match:      {match}")
    
    @staticmethod
    def print_content_quality(metrics: Dict):
        """Print content quality metrics."""
        print(f"\n📝 CONTENT QUALITY:")
        avg_len = metrics['avg_content_length']
        print(f"  Avg Content Length:  {avg_len:.0f} chars")
        non_empty = metrics['non_empty_count']
        print(f"  Non-Empty Sections:  {non_empty:,}")
        quality = metrics['content_quality_pct']
        print(f"  Content Quality:     {quality:.1f}%")
    
    @staticmethod
    def print_page_coverage(page_cov: Dict):
        """Print page coverage information."""
        total_pages = page_cov.get("total_pages", 0)
        pages_covered = page_cov.get("pages_covered", 0)
        coverage_pct = page_cov.get("coverage_percentage", 0)
        
        print(f"\n  📄 Page Coverage:")
        print(f"    Total Pages:       {total_pages:,}")
        print(f"    Pages Covered:     {pages_covered:,}")
        missing = page_cov.get('pages_missing', 0)
        print(f"    Pages Missing:     {missing:,}")
        print(f"    Coverage:          {coverage_pct}%")
        
        status = ReportPrinter._get_coverage_status(coverage_pct)
        print(f"    Status:            {status}")
    
    @staticmethod
    def _get_coverage_status(coverage_pct: float) -> str:
        """Determine coverage status based on percentage."""
        # Define coverage thresholds in order of priority (highest first)
        thresholds = [
            (95, "✓ EXCELLENT"),
            (80, "✓ GOOD"),
            (60, "⚠ FAIR"),
        ]
        
        for threshold, status in thresholds:
            if coverage_pct >= threshold:
                return status
        
        return "✗ POOR"
    
    @staticmethod
    def print_content_analysis(content_analysis: Dict):
        """Print content analysis."""
        print(f"\n  📊 Content Analysis:")
        with_content = content_analysis.get(
            'sections_with_content',
            0
        )
        print(f"    With Content:      {with_content:,}")
        without = content_analysis.get('sections_without_content', 0)
        print(f"    Without Content:   {without:,}")
        avg_len = content_analysis.get('average_content_length', 0)
        print(f"    Avg Length:        {avg_len:.0f}")
    
    @staticmethod
    def print_toc_analysis(toc_analysis: Dict):
        """Print TOC analysis."""
        print(f"\n  🗂️  TOC Analysis:")
        total = toc_analysis.get('total_sections', 0)
        print(f"    Total Sections:    {total:,}")
        levels = toc_analysis.get('hierarchy_levels', 0)
        print(f"    Hierarchy Levels:  {levels}")
        depth = toc_analysis.get('max_depth', 0)
        print(f"    Max Depth:         {depth}")
    
    @staticmethod
    def print_quality_metrics(metrics: Dict):
        """Print quality metrics."""
        print(f"\n  🎯 Quality Metrics:")
        page_cov = metrics.get('page_coverage_percentage', 0)
        print(f"    Page Coverage:     {page_cov}%")
        content_qual = metrics.get('content_quality_percentage', 0)
        print(f"    Content Quality:   {content_qual:.1f}%")
        overall = metrics.get('overall_quality_score', 0)
        print(f"    Overall Score:     {overall:.1f}%")
    
    @staticmethod
    def print_samples(
        toc_samples: List[Dict],
        spec_samples: List[Dict]
    ):
        """Print sample data."""
        print("\n🔍 SAMPLE DATA (First 3 entries):")
        
        print("\n  TOC Sample:")
        for i, entry in enumerate(toc_samples, 1):
            sec_id = entry.get("section_id", "N/A")
            title = entry.get("title", "N/A")[:40]
            page = entry.get("page", "N/A")
            print(f"    {i}. [{sec_id}] {title}... (p.{page})")
        
        print("\n  Content Sample:")
        for i, entry in enumerate(spec_samples, 1):
            sec_id = entry.get("section_id", "N/A")
            content = entry.get("content", "N/A")[:40]
            length = len(entry.get("content", ""))
            print(f"    {i}. [{sec_id}] {content}... ({length} chars)")
    
    @staticmethod
    def print_final_status(
        toc_count: int,
        spec_count: int,
        validation_data: Dict
    ):
        """Print final status by delegating to appropriate handler."""
        print("\n" + "="*70)
        
        if toc_count > 5000 and spec_count > 5000:
            ReportPrinter._print_success_status(validation_data)
        else:
            ReportPrinter._print_error_status(toc_count, spec_count)
        
        print("="*70)
    
    @staticmethod
    def _print_success_status(validation_data: Dict):
        """Print success status based on validation data."""
        if validation_data:
            status = validation_data.get("validation_status", "UNKNOWN")
            metrics = validation_data.get("detailed_metrics", {})
            overall = metrics.get("overall_quality_score", 0)
            ReportPrinter._print_success_message(status, overall)
        else:
            print("✓ SUCCESS: Files generated!")
            print("⚠ WARNING: Validation report missing.")
    
    @staticmethod
    def _print_error_status(toc_count: int, spec_count: int):
        """Print error status for insufficient sections."""
        print("✗ ERROR: Insufficient sections extracted.")
        print(
            f"  Expected: >5000, Got: "
            f"TOC={toc_count}, Content={spec_count}"
        )
    
    @staticmethod
    def _print_success_message(status: str, overall: float):
        """Print success message based on status and score."""
        # Define success criteria in order of priority
        success_criteria = [
            (
                "✓ SUCCESS: EXCELLENT extraction quality!",
                lambda s, o: s == "EXCELLENT" or o >= 90,
            ),
            (
                "✓ SUCCESS: GOOD extraction quality!",
                lambda s, o: s == "GOOD" or o >= 75,
            ),
        ]
        
        for message, condition in success_criteria:
            if condition(status, overall):
                print(message)
                print(f"  Overall Score: {overall:.1f}%")
                return
        
        print("⚠ PARTIAL: Extraction completed with warnings.")
        print(f"  Overall Score: {overall:.1f}%")


def check_sections():
    """Main validation function with reduced complexity."""
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    output_dir = os.path.join(project_root, "data", "output")
    
    checker = FileChecker(output_dir)
    files_status = checker.check_files()
    
    if not checker.all_required_exist():
        _handle_missing_files(checker, files_status)
        return
    
    _process_and_print_report(checker, files_status)


def _handle_missing_files(checker: FileChecker, files_status: Dict[str, bool]):
    """Handle case when required files are missing."""
    print("="*70)
    print("❌ ERROR: Required files missing!")
    print("="*70)
    if not files_status["TOC"]:
        print(f"Missing: {checker.toc_file}")
    if not files_status["Spec"]:
        print(f"Missing: {checker.spec_file}")
    print("\nRun: python src/usb_pd_parser.py")
    print("="*70)


def _process_and_print_report(
    checker: FileChecker,
    files_status: Dict[str, bool]
):
    """Process data and print the full report."""
    analyzer = DataAnalyzer(checker.toc_file, checker.spec_file)
    toc_count, toc_samples = analyzer.analyze_toc()
    spec_count, spec_samples, spec_metrics = analyzer.analyze_spec()
    
    val_analyzer = ValidationAnalyzer(checker.validation_file)
    has_validation = val_analyzer.load_data()
    
    printer = ReportPrinter()
    printer.print_header()
    printer.print_file_status(files_status)
    printer.print_extraction_stats(toc_count, spec_count)
    printer.print_content_quality(spec_metrics)
    
    if has_validation:
        _print_validation_analysis(printer, val_analyzer)
    
    printer.print_samples(toc_samples, spec_samples)
    printer.print_final_status(toc_count, spec_count, val_analyzer.data)


def _print_validation_analysis(
    printer: ReportPrinter,
    val_analyzer: ValidationAnalyzer
):
    """Print detailed validation analysis."""
    print("\n📋 VALIDATION REPORT ANALYSIS:")
    printer.print_page_coverage(val_analyzer.get_page_coverage())
    printer.print_content_analysis(val_analyzer.get_content_analysis())
    printer.print_toc_analysis(val_analyzer.get_toc_analysis())
    printer.print_quality_metrics(val_analyzer.get_metrics())
    print(f"\n  ✨ Validation Status: {val_analyzer.get_status()}")


if __name__ == "__main__":
    check_sections()