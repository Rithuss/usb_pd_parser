"""
Enhanced Section Validation Script - REFACTORED
Fixed: 219-line function broken into 15 small functions
"""
import json
import os


class FileChecker:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.toc_file = os.path.join(output_dir, "usb_pd_toc.jsonl")
        self.spec_file = os.path.join(output_dir, "usb_pd_spec.jsonl")
        self.validation_file = os.path.join(output_dir, "validation_report.json")
    
    def check_files_exist(self) -> dict:
        return {
            "TOC": os.path.exists(self.toc_file),
            "Spec": os.path.exists(self.spec_file),
            "Validation": os.path.exists(self.validation_file)
        }
    
    def print_missing_files(self, files_status: dict):
        print("="*70)
        print("❌ ERROR: Required files missing!")
        print("="*70)
        if not files_status["TOC"]:
            print(f"Missing: {self.toc_file}")
        if not files_status["Spec"]:
            print(f"Missing: {self.spec_file}")
        print("\nRun: python src/usb_pd_parser.py")
        print("="*70)


class FileLoader:
    @staticmethod
    def load_toc(filepath: str) -> tuple:
        toc_count = 0
        toc_samples = []
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    toc_count += 1
                    if i < 3:
                        toc_samples.append(json.loads(line))
        return toc_count, toc_samples
    
    @staticmethod
    def load_spec(filepath: str) -> tuple:
        spec_count = 0
        spec_samples = []
        total_content_length = 0
        non_empty_count = 0
        
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    spec_count += 1
                    entry = json.loads(line)
                    content = entry.get("content", "")
                    total_content_length += len(content)
                    
                    if content.strip():
                        non_empty_count += 1
                    
                    if i < 3:
                        spec_samples.append(entry)
        
        return spec_count, spec_samples, total_content_length, non_empty_count
    
    @staticmethod
    def load_validation(filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


class MetricsCalculator:
    @staticmethod
    def calc_content_metrics(spec_count: int, total_length: int, non_empty: int) -> tuple:
        avg = total_length / spec_count if spec_count > 0 else 0
        quality = non_empty / spec_count * 100 if spec_count > 0 else 0
        return avg, quality
    
    @staticmethod
    def determine_status(coverage_pct: float) -> str:
        if coverage_pct >= 95:
            return "✓ EXCELLENT"
        elif coverage_pct >= 80:
            return "✓ GOOD"
        elif coverage_pct >= 60:
            return "⚠ FAIR"
        else:
            return "✗ POOR"


class ReportPrinter:
    @staticmethod
    def print_header():
        print("="*70)
        print("USB PD PARSER - VALIDATION REPORT")
        print("="*70)
    
    @staticmethod
    def print_file_status(files_status: dict):
        print("\n📊 FILE STATUS:")
        for name, exists in files_status.items():
            status = "✓ Found" if exists else "✗ Missing"
            print(f"  {status:12} - {name}")
    
    @staticmethod
    def print_extraction_stats(toc_count: int, spec_count: int):
        print("\n📈 EXTRACTION STATISTICS:")
        print(f"  TOC Sections:        {toc_count:,}")
        print(f"  Content Sections:    {spec_count:,}")
        print(f"  Sections Match:      {'✓ Yes' if toc_count == spec_count else '✗ No'}")
    
    @staticmethod
    def print_content_quality(avg_length: float, non_empty: int, quality_pct: float):
        print(f"\n📝 CONTENT QUALITY:")
        print(f"  Avg Content Length:  {avg_length:.0f} chars")
        print(f"  Non-Empty Sections:  {non_empty:,}")
        print(f"  Content Quality:     {quality_pct:.1f}%")
    
    @staticmethod
    def print_page_coverage(page_cov: dict):
        total = page_cov.get("total_pages", 0)
        covered = page_cov.get("pages_covered", 0)
        coverage = page_cov.get("coverage_percentage", 0)
        
        print(f"\n  📄 Page Coverage:")
        print(f"    Total Pages:       {total:,}")
        print(f"    Pages Covered:     {covered:,}")
        print(f"    Pages Missing:     {page_cov.get('pages_missing', 0):,}")
        print(f"    Coverage:          {coverage}%")
        print(f"    Status:            {MetricsCalculator.determine_status(coverage)}")
    
    @staticmethod
    def print_samples(toc_samples: list, spec_samples: list):
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
    def print_final_status(toc_count: int, spec_count: int, validation_data: dict):
        print("\n" + "="*70)
        
        if toc_count > 5000 and spec_count > 5000:
            if validation_data:
                status = validation_data.get("validation_status", "UNKNOWN")
                metrics = validation_data.get("detailed_metrics", {})
                overall = metrics.get("overall_quality_score", 0)
                
                if status == "EXCELLENT" or overall >= 90:
                    print("✓ SUCCESS: EXCELLENT extraction quality!")
                    print(f"  Overall Score: {overall:.1f}%")
                elif status == "GOOD" or overall >= 75:
                    print("✓ SUCCESS: GOOD extraction quality!")
                    print(f"  Overall Score: {overall:.1f}%")
                else:
                    print("⚠ PARTIAL: Extraction completed with warnings.")
                    print(f"  Overall Score: {overall:.1f}%")
            else:
                print("✓ SUCCESS: Files generated!")
                print("⚠ WARNING: Validation report missing.")
        else:
            print("✗ ERROR: Insufficient sections extracted.")
            print(f"  Expected: >5000, Got: TOC={toc_count}, Content={spec_count}")
        
        print("="*70)


def check_sections():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "data", "output")
    
    checker = FileChecker(output_dir)
    files_status = checker.check_files_exist()
    
    if not files_status["TOC"] or not files_status["Spec"]:
        checker.print_missing_files(files_status)
        return
    
    ReportPrinter.print_header()
    
    loader = FileLoader()
    toc_count, toc_samples = loader.load_toc(checker.toc_file)
    spec_count, spec_samples, total_length, non_empty = loader.load_spec(checker.spec_file)
    
    avg_length, quality_pct = MetricsCalculator.calc_content_metrics(
        spec_count, total_length, non_empty
    )
    
    validation_data = None
    if files_status["Validation"]:
        validation_data = loader.load_validation(checker.validation_file)
    
    printer = ReportPrinter()
    printer.print_file_status(files_status)
    printer.print_extraction_stats(toc_count, spec_count)
    printer.print_content_quality(avg_length, non_empty, quality_pct)
    
    if validation_data:
        print("\n📋 VALIDATION REPORT ANALYSIS:")
        summary = validation_data.get("summary", {})
        page_cov = summary.get("page_coverage", {})
        printer.print_page_coverage(page_cov)
    
    printer.print_samples(toc_samples, spec_samples)
    printer.print_final_status(toc_count, spec_count, validation_data)


if __name__ == "__main__":
    check_sections()