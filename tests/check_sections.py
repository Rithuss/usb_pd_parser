"""
Enhanced Section Validation Script
PEP8-compliant version (line length & code smells fixed)
"""

import json
import os


class FileChecker:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.toc_file = os.path.join(output_dir, "usb_pd_toc.jsonl")
        self.spec_file = os.path.join(output_dir, "usb_pd_spec.jsonl")
        self.validation_file = os.path.join(
            output_dir,
            "validation_report.json"
        )

    def check_files_exist(self) -> dict:
        return {
            "TOC": os.path.exists(self.toc_file),
            "Spec": os.path.exists(self.spec_file),
            "Validation": os.path.exists(self.validation_file),
        }

    def print_missing_files(self, files_status: dict):
        print("=" * 70)
        print("❌ ERROR: Required files missing!")
        print("=" * 70)

        if not files_status["TOC"]:
            print(f"Missing: {self.toc_file}")

        if not files_status["Spec"]:
            print(f"Missing: {self.spec_file}")

        print("\nRun: python src/app/run_parser.py")
        print("=" * 70)


class FileLoader:
    @staticmethod
    def load_toc(filepath: str) -> tuple:
        toc_count = 0
        toc_samples = []

        with open(filepath, "r", encoding="utf-8") as file:
            for index, line in enumerate(file):
                if line.strip():
                    toc_count += 1
                    if index < 3:
                        toc_samples.append(json.loads(line))

        return toc_count, toc_samples

    @staticmethod
    def load_spec(filepath: str) -> tuple:
        spec_count = 0
        spec_samples = []
        total_length = 0
        non_empty = 0

        with open(filepath, "r", encoding="utf-8") as file:
            for index, line in enumerate(file):
                if not line.strip():
                    continue

                spec_count += 1
                entry = json.loads(line)
                content = entry.get("content", "")
                total_length += len(content)

                if content.strip():
                    non_empty += 1

                if index < 3:
                    spec_samples.append(entry)

        return spec_count, spec_samples, total_length, non_empty

    @staticmethod
    def load_validation(filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)


class MetricsCalculator:
    @staticmethod
    def calc_content_metrics(
        spec_count: int,
        total_length: int,
        non_empty: int
    ) -> tuple:
        average = (
            total_length / spec_count if spec_count > 0 else 0
        )
        quality = (
            non_empty / spec_count * 100 if spec_count > 0 else 0
        )
        return average, quality

    @staticmethod
    def determine_status(coverage_pct: float) -> str:
        if coverage_pct >= 95:
            return "✓ EXCELLENT"
        if coverage_pct >= 80:
            return "✓ GOOD"
        if coverage_pct >= 60:
            return "⚠ FAIR"
        return "✗ POOR"


class ReportPrinter:
    @staticmethod
    def print_header():
        print("=" * 70)
        print("USB PD PARSER - VALIDATION REPORT")
        print("=" * 70)

    @staticmethod
    def print_file_status(files_status: dict):
        print("\n📊 FILE STATUS:")
        for name, exists in files_status.items():
            status = "✓ Found" if exists else "✗ Missing"
            print(f"  {status:12} - {name}")

    @staticmethod
    def print_extraction_stats(toc_count: int, spec_count: int):
        print("\n📈 EXTRACTION STATISTICS:")
        print(f"  TOC Sections:     {toc_count:,}")
        print(f"  Content Sections: {spec_count:,}")

    @staticmethod
    def print_content_quality(
        avg_length: float,
        non_empty: int,
        quality_pct: float
    ):
        print("\n📝 CONTENT QUALITY:")
        print(f"  Avg Content Length: {avg_length:.0f} chars")
        print(f"  Non-Empty Sections: {non_empty:,}")
        print(f"  Content Quality:    {quality_pct:.1f}%")

    @staticmethod
    def print_page_coverage(page_cov: dict):
        total_pages = page_cov.get("total_pages", 0)
        pages_covered = page_cov.get("pages_covered", 0)
        pages_missing = page_cov.get("pages_missing", 0)
        coverage = page_cov.get("coverage_percentage", 0)

        status = MetricsCalculator.determine_status(coverage)

        print("\n📄 PAGE COVERAGE:")
        print(f"  Total Pages:   {total_pages:,}")
        print(f"  Pages Covered: {pages_covered:,}")
        print(f"  Pages Missing: {pages_missing:,}")
        print(f"  Coverage:      {coverage}%")
        print(f"  Status:        {status}")

    @staticmethod
    def print_samples(toc_samples: list, spec_samples: list):
        print("\n🔍 SAMPLE DATA:")

        print("\n  TOC Sample:")
        for index, entry in enumerate(toc_samples, start=1):
            section_id = entry.get("section_id", "N/A")
            title = entry.get("title", "")[:40]
            page = entry.get("page", "N/A")
            print(f"    {index}. [{section_id}] {title}... (p.{page})")

        print("\n  Content Sample:")
        for index, entry in enumerate(spec_samples, start=1):
            section_id = entry.get("section_id", "N/A")
            content = entry.get("content", "")[:40]
            length = len(entry.get("content", ""))
            print(
                f"    {index}. [{section_id}] "
                f"{content}... ({length} chars)"
            )


def check_sections():
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    output_dir = os.path.join(project_root, "data", "output")

    checker = FileChecker(output_dir)
    files_status = checker.check_files_exist()

    if not files_status["TOC"] or not files_status["Spec"]:
        checker.print_missing_files(files_status)
        return

    ReportPrinter.print_header()

    toc_count, toc_samples = FileLoader.load_toc(checker.toc_file)
    (
        spec_count,
        spec_samples,
        total_length,
        non_empty
    ) = FileLoader.load_spec(checker.spec_file)

    avg_length, quality_pct = MetricsCalculator.calc_content_metrics(
        spec_count,
        total_length,
        non_empty
    )

    validation_data = (
        FileLoader.load_validation(checker.validation_file)
        if files_status["Validation"]
        else {}
    )

    ReportPrinter.print_file_status(files_status)
    ReportPrinter.print_extraction_stats(toc_count, spec_count)
    ReportPrinter.print_content_quality(
        avg_length,
        non_empty,
        quality_pct
    )

    if validation_data:
        summary = validation_data.get("summary", {})
        page_cov = summary.get("page_coverage", {})
        ReportPrinter.print_page_coverage(page_cov)

    ReportPrinter.print_samples(toc_samples, spec_samples)


if __name__ == "__main__":
    check_sections()
