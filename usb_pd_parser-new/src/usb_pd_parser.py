"""
USB Power Delivery Specification Parser 
"""
import json
import os
import logging
import pdfplumber
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple


# Configure logging for extraction tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseEntity(ABC):
    """Abstract base class demonstrating ABSTRACTION."""
    
    def __init__(self, doc_title: str):
        self._doc_title = doc_title
        self._metadata = {}
    
    @property
    def doc_title(self) -> str:
        return self._doc_title
    
    @abstractmethod
    def validate(self) -> bool:
        pass
    
    def add_metadata(self, key: str, value: Any):
        self._metadata[key] = value
    
    def get_metadata(self) -> Dict:
        return self._metadata.copy()


class BaseExtractor(ABC):
    """Abstract base class for all extractors."""
    
    def __init__(self, text_data: Dict, doc_title: str):
        self._text_data = text_data
        self._doc_title = doc_title
        self._total_pages = len(text_data)
        self._extracted_items = []
    
    @abstractmethod
    def extract(self) -> List[Dict]:
        pass
    
    def get_page_count(self) -> int:
        return self._total_pages
    
    def get_extracted_count(self) -> int:
        return len(self._extracted_items)
    
    @property
    def text_data(self) -> Dict:
        return self._text_data


class PDFParser:
    """PDF Parser with enhanced page tracking."""
    
    def __init__(self, pdf_path: str):
        self._pdf_path = pdf_path
        self._doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        self._total_pages = 0
        self._pages_processed = 0
        self._pages_with_content = 0
        self._pages_without_content = 0
        self._extraction_stats = {}

    @property
    def doc_title(self) -> str:
        return self._doc_title

    def extract_text(self) -> Dict[int, str]:
        """Extract text into a mapping of page number -> text.

        Keeps the existing behavior (tracking pages, printing
        progress and summary) but reduces redundant attribute
        access and clarifies intent via local variables and
        explanatory comments.
        """

        # Print a short header to indicate extraction start
        self._print_extraction_header()

        # Open PDF once and keep a local reference to pages to
        # avoid repeated attribute lookups on the context manager
        with pdfplumber.open(self._pdf_path) as pdf:
            pages = pdf.pages
            self._total_pages = len(pages)
            print(f"Total pages in PDF: {self._total_pages}")

            # Delegate page processing to the helper which
            # increments internal counters and returns the
            # page->text mapping.
            text_mapping = self._process_all_pages(pages)

        # Compute and print aggregate statistics collected
        # during page processing.
        self._calculate_extraction_stats()
        self._print_extraction_summary()

        return text_mapping
    
    def _print_extraction_header(self):
        """Print extraction header."""
        print("\n" + "="*60)
        print("PDF EXTRACTION STARTED")
        print("="*60)
    
    def _process_all_pages(self, pages) -> Dict[int, str]:
        """Process all PDF pages and collect text data."""
        text_data = {}
        failed_pages = []
        empty_pages = []
        
        for page_number, page in enumerate(pages, start=1):
            self._pages_processed += 1
            try:
                extracted_text = page.extract_text()
                result_text = self._process_single_page(extracted_text, page_number)
                text_data[page_number] = result_text
                
                # Log empty pages for debugging
                if not extracted_text or not extracted_text.strip():
                    empty_pages.append(page_number)
                    logger.debug(f"Page {page_number}: No text extracted")
                    
            except Exception as e:
                failed_pages.append(page_number)
                text_data[page_number] = ""
                logger.warning(f"Page {page_number}: Extraction failed - {str(e)}")
            
            self._print_progress(page_number)
        
        # Log summary of empty and failed pages
        self._log_extraction_issues(empty_pages, failed_pages)
        
        return text_data
    
    def _print_progress(self, page_number: int):
        """Print progress update every 100 pages."""
        if page_number % 100 == 0:
            print(f"Processed: {page_number}/{self._total_pages} pages...")
    
    def _log_extraction_issues(self, empty_pages: List[int], failed_pages: List[int]):
        """Log information about pages with extraction issues."""
        if empty_pages:
            logger.info(f"Pages with no text content: {len(empty_pages)} pages")
            if len(empty_pages) <= 20:
                logger.debug(f"Empty page numbers: {empty_pages}")
            else:
                logger.debug(f"First 20 empty pages: {empty_pages[:20]}")
        
        if failed_pages:
            logger.error(f"Pages with extraction errors: {len(failed_pages)} pages")
            logger.error(f"Failed page numbers: {failed_pages}")
        
        # Ensure all pages were attempted
        total_attempted = len(empty_pages) + len(failed_pages) + self._pages_with_content
        if total_attempted == self._total_pages:
            logger.info(f"✓ All {self._total_pages} pages processed successfully")
        else:
            logger.warning(f"⚠ Only {total_attempted}/{self._total_pages} pages processed")
    
    def _process_single_page(self, text: str, page_number: int = None) -> str:
        """Process single page text and track statistics."""
        if text and text.strip():
            self._pages_with_content += 1
            return text
        else:
            self._pages_without_content += 1
            return ""
    
    def _calculate_extraction_stats(self):
        """Calculate extraction statistics."""
        if self._total_pages > 0:
            success_rate = (
                self._pages_with_content / self._total_pages * 100
            )
        else:
            success_rate = 0
        
        self._extraction_stats = {
            "total_pages": self._total_pages,
            "pages_processed": self._pages_processed,
            "pages_with_content": self._pages_with_content,
            "pages_without_content": self._pages_without_content,
            "success_rate": round(success_rate, 2)
        }
    
    def _print_extraction_summary(self):
        """Print extraction summary."""
        stats = self._extraction_stats
        print(f"\nExtraction Complete:")
        print(f"  Pages with content: {self._pages_with_content}")
        print(
            f"  Pages without content: "
            f"{self._pages_without_content}"
        )
        print(f"  Success rate: {stats['success_rate']}%")
        print("="*60 + "\n")
        
        # Log detailed extraction statistics
        logger.info(f"Extraction Summary:")
        logger.info(f"  Total pages: {stats['total_pages']}")
        logger.info(f"  Pages processed: {stats['pages_processed']}")
        logger.info(f"  Pages with content: {stats['pages_with_content']}")
        logger.info(f"  Pages without content: {stats['pages_without_content']}")
        logger.info(f"  Success rate: {stats['success_rate']}%")
    
    def get_page_coverage_stats(self) -> Dict:
        """Return comprehensive page statistics."""
        if self._total_pages > 0:
            coverage_pct = round(
                (self._pages_with_content / self._total_pages * 100),
                2
            )
        else:
            coverage_pct = 0
        
        return {
            "total_pages": self._total_pages,
            "pages_covered": self._pages_with_content,
            "pages_missing": self._pages_without_content,
            "coverage_percentage": coverage_pct,
            "extraction_success_rate": 
                self._extraction_stats.get("success_rate", 0)
        }


class TOCExtractor(BaseExtractor):
    """Table of Contents extractor."""
    
    def extract(self) -> List[Dict]:
        """Extract TOC entries with enhanced pattern matching."""
        self._extracted_items = []
        
        for page_num, content in self._text_data.items():
            if content:
                self._process_page_content(content, page_num)
        
        return self._extracted_items
    
    def _process_page_content(self, content: str, page_num: int):
        """Process content from a single page."""
        lines = content.split("\n")
        for line in lines:
            self._handle_toc_line(line.strip(), page_num)
    
    def _handle_toc_line(self, line_stripped: str, page_num: int):
        """Handle a single TOC line: skip empty or create entry if section."""
        if not line_stripped:
            return
        
        if self._is_section_line(line_stripped):
            entry = self._create_toc_entry(line_stripped, page_num)
            self._extracted_items.append(entry)
    
    def _is_section_line(self, line: str) -> bool:
        """Check if line is a section."""
        return line and len(line) > 0 and line[0].isdigit()
    
    def _create_toc_entry(
        self,
        line: str,
        page_num: int
    ) -> Dict:
        """Create TOC entry from line."""
        section_id, title = self._parse_section_line(line)
        level = section_id.count('.') + 1
        parent_id = self._get_parent_id(section_id)
        
        return {
            "doc_title": self._doc_title,
            "section_id": section_id,
            "title": title,
            "page": page_num,
            "level": level,
            "parent_id": parent_id,
            "full_path": f"{section_id} {title}"
        }
    
    def _parse_section_line(self, line: str) -> Tuple[str, str]:
        """Parse section line into ID and title."""
        parts = line.split(maxsplit=1)
        section_id = parts[0].rstrip('.')
        title = parts[1] if len(parts) > 1 else ""
        return section_id, title
    
    def _get_parent_id(self, section_id: str) -> str:
        """Get parent section ID."""
        if '.' in section_id:
            return '.'.join(section_id.split('.')[:-1])
        return None
    
    def validate(self) -> bool:
        return True


class ContentExtractor(BaseExtractor):
    """Content extractor with enhanced extraction."""
    
    def extract(self) -> List[Dict]:
        """Extract content with improved coverage."""
        self._extracted_items = []
        section_state = {"current": None, "buffer": []}
        
        for page_num, content in self._text_data.items():
            if content:
                self._process_page(content, page_num, section_state)
        
        self._save_section(section_state["current"], section_state["buffer"])
        return self._extracted_items
    
    def _process_page(self, content: str, page_num: int, section_state: Dict):
        """Process content from a single page and update section state."""
        lines = content.split("\n")
        for line in lines:
            line_stripped = line.strip()
            self._handle_content_line(line_stripped, section_state)
    
    def _handle_content_line(
        self,
        line_stripped: str,
        section_state: Dict
    ):
        """Handle a single content line: check for new section or append to buffer."""
        if self._is_new_section(line_stripped):
            self._save_section(section_state["current"], section_state["buffer"])
            self._start_new_section(line_stripped, section_state)
        elif line_stripped:
            section_state["buffer"].append(line_stripped)
    
    def _is_new_section(self, line: str) -> bool:
        """Check if line starts new section."""
        return line and len(line) > 0 and line[0].isdigit()
    
    def _start_new_section(self, line: str, section_state: Dict):
        """Start new section and update state."""
        parts = line.split(maxsplit=1)
        section_state["current"] = parts[0].rstrip('.')
        section_state["buffer"] = [parts[1]] if len(parts) > 1 else []
    
    def _save_section(self, section_id: str, buffer: List[str]):
        """Save section to extracted items."""
        if section_id and buffer:
            content_text = " ".join(buffer).strip()
            if content_text:
                self._extracted_items.append({
                    "doc_title": self._doc_title,
                    "section_id": section_id,
                    "content": content_text
                })
    
    def validate(self) -> bool:
        return len(self._extracted_items) > 0
    
    def get_content_stats(self) -> Dict:
        """Get content quality metrics."""
        total = len(self._extracted_items)
        non_empty = self._count_non_empty_sections()
        avg_length = self._calculate_average_length(total)
        quality = self._determine_quality_level(non_empty, total)
        
        return {
            "total_sections": total,
            "sections_with_content": non_empty,
            "sections_without_content": total - non_empty,
            "average_content_length": round(avg_length, 2),
            "content_quality": quality
        }
    
    def _count_non_empty_sections(self) -> int:
        """Count sections with non-empty content."""
        return sum(
            1 for item in self._extracted_items
            if item.get("content", "").strip()
        )
    
    def _calculate_average_length(self, total: int) -> float:
        """Calculate average content length across sections."""
        if total == 0:
            return 0.0
        return sum(
            len(item.get("content", ""))
            for item in self._extracted_items
        ) / total
    
    def _determine_quality_level(self, non_empty: int, total: int) -> str:
        """Determine quality level based on content completeness."""
        if total == 0:
            return "Fair"
        return "Good" if non_empty > total * 0.9 else "Fair"


class ValidationReportGenerator:
    """Generates comprehensive validation report."""
    
    def __init__(
        self,
        toc_entries: List[Dict],
        content_entries: List[Dict],
        page_stats: Dict,
        doc_title: str
    ):
        self._toc_entries = toc_entries
        self._content_entries = content_entries
        self._page_stats = page_stats
        self._doc_title = doc_title
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report."""
        from datetime import datetime
        
        return {
            "document": self._doc_title,
            "validation_date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "summary": self._create_summary(),
            "toc_analysis": self._analyze_toc(),
            "content_analysis": self._analyze_content(),
            "validation_status": self._determine_status(),
            "detailed_metrics": self._calculate_metrics()
        }
    
    def _create_summary(self) -> Dict:
        """Create report summary."""
        return {
            "total_toc_sections": len(self._toc_entries),
            "total_content_sections": len(self._content_entries),
            "sections_matched": self._count_matched_sections(),
            "page_coverage": self._page_stats
        }
    
    def _count_matched_sections(self) -> int:
        """Count sections in both TOC and content."""
        toc_ids = {e["section_id"] for e in self._toc_entries}
        content_ids = {
            e["section_id"] for e in self._content_entries
        }
        return len(toc_ids.intersection(content_ids))
    
    def _analyze_toc(self) -> Dict:
        """Analyze TOC structure."""
        levels = {}
        for entry in self._toc_entries:
            level = entry["level"]
            levels[level] = levels.get(level, 0) + 1
        
        return {
            "total_sections": len(self._toc_entries),
            "hierarchy_levels": len(levels),
            "sections_per_level": levels,
            "max_depth": max(levels.keys()) if levels else 0
        }
    
    def _analyze_content(self) -> Dict:
        """Analyze content extraction quality."""
        non_empty = [
            e for e in self._content_entries
            if e.get("content", "").strip()
        ]
        
        total_chars = sum(
            len(e.get("content", ""))
            for e in self._content_entries
        )
        avg_length = self._compute_average_content_length(total_chars)
        
        return {
            "total_sections": len(self._content_entries),
            "sections_with_content": len(non_empty),
            "sections_without_content": (
                len(self._content_entries) - len(non_empty)
            ),
            "average_content_length": round(avg_length, 2),
            "total_characters": total_chars
        }
    
    def _compute_average_content_length(self, total_chars: int) -> float:
        """Compute average content length."""
        if not self._content_entries:
            return 0.0
        return total_chars / len(self._content_entries)
    
    def _calculate_metrics(self) -> Dict:
        """Calculate comprehensive quality metrics."""
        page_coverage = self._page_stats.get("coverage_percentage", 0)
        content_quality = self._compute_content_quality()
        overall_score = (page_coverage + content_quality) / 2
        
        return {
            "page_coverage_percentage": page_coverage,
            "content_quality_percentage": round(content_quality, 2),
            "toc_completeness": len(self._toc_entries) > 1000,
            "overall_quality_score": round(overall_score, 2)
        }
    
    def _compute_content_quality(self) -> float:
        """Compute content quality percentage."""
        if not self._content_entries:
            return 0.0
        
        quality_sections = [
            e for e in self._content_entries
            if e.get("content", "").strip()
        ]
        return len(quality_sections) / len(self._content_entries) * 100
    
    def _determine_status(self) -> str:
        """Determine overall validation status based on thresholds."""
        coverage = self._page_stats.get("coverage_percentage", 0)
        toc_count = len(self._toc_entries)
        content_count = len(self._content_entries)
        
        if self._meets_excellent_threshold(coverage, toc_count, content_count):
            return "EXCELLENT"
        if self._meets_good_threshold(coverage, toc_count):
            return "GOOD"
        if self._meets_fair_threshold(coverage):
            return "FAIR"
        
        return "NEEDS_IMPROVEMENT"
    
    def _meets_excellent_threshold(self, coverage: float, toc_count: int, content_count: int) -> bool:
        """Check if metrics meet EXCELLENT criteria."""
        return coverage >= 95 and toc_count > 5000 and content_count > 5000
    
    def _meets_good_threshold(self, coverage: float, toc_count: int) -> bool:
        """Check if metrics meet GOOD criteria."""
        return coverage >= 85 and toc_count > 1000
    
    def _meets_fair_threshold(self, coverage: float) -> bool:
        """Check if metrics meet FAIR criteria."""
        return coverage >= 70


class USBPDParserApp:
    """Main application orchestrator."""
    
    def __init__(self, pdf_path: str, output_dir: str):
        self._pdf_path = pdf_path
        self._output_dir = output_dir
        self._doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        self._parser = None
        self._toc_extractor = None
        self._content_extractor = None
        self._validation_generator = None

    def run(self):
        """Main execution orchestrator."""
        self._print_header()
        
        text_data = self._parse_pdf()
        toc_entries = self._extract_toc(text_data)
        content_entries = self._extract_content(text_data)
        validation_report = self._generate_validation(
            toc_entries,
            content_entries
        )
        
        self._print_final_summary(
            len(toc_entries),
            len(content_entries),
            validation_report
        )
    
    def _print_header(self):
        """Print application header."""
        print("\n" + "="*60)
        print("USB PD PARSER - ENHANCED OOP VERSION")
        print("="*60)
    
    def _parse_pdf(self) -> Dict[int, str]:
        """Parse PDF and return text data."""
        print("\n[STEP 1] Parsing PDF...")
        self._parser = PDFParser(self._pdf_path)
        return self._parser.extract_text()
    
    def _extract_toc(self, text_data: Dict[int, str]) -> List[Dict]:
        """Extract TOC entries."""
        print("\n[STEP 2] Extracting Table of Contents...")
        self._toc_extractor = TOCExtractor(
            text_data,
            self._doc_title
        )
        toc_entries = self._toc_extractor.extract()
        self.save_jsonl(toc_entries, "usb_pd_toc.jsonl")
        print(f"✓ TOC extracted: {len(toc_entries)} sections")
        return toc_entries
    
    def _extract_content(
        self,
        text_data: Dict[int, str]
    ) -> List[Dict]:
        """Extract content entries."""
        print("\n[STEP 3] Extracting Specification Content...")
        self._content_extractor = ContentExtractor(
            text_data,
            self._doc_title
        )
        content_entries = self._content_extractor.extract()
        self.save_jsonl(content_entries, "usb_pd_spec.jsonl")
        
        content_stats = self._content_extractor.get_content_stats()
        print(f"✓ Content extracted: {len(content_entries)} sections")
        print(f"  Quality: {content_stats['content_quality']}")
        avg_len = content_stats['average_content_length']
        print(f"  Avg length: {avg_len:.0f} chars")
        return content_entries
    
    def _generate_validation(
        self,
        toc_entries: List[Dict],
        content_entries: List[Dict]
    ) -> Dict:
        """Generate validation report."""
        print("\n[STEP 4] Generating Validation Report...")
        page_stats = self._parser.get_page_coverage_stats()
        
        self._validation_generator = ValidationReportGenerator(
            toc_entries,
            content_entries,
            page_stats,
            self._doc_title
        )
        
        validation_report = (
            self._validation_generator.generate_report()
        )
        self.save_json(validation_report, "validation_report.json")
        
        print(f"✓ Validation report generated")
        status = validation_report['validation_status']
        print(f"  Status: {status}")
        
        return validation_report

    def save_jsonl(self, data: List[Dict], filename: str):
        """Save data in JSONL format."""
        try:
            os.makedirs(self._output_dir, exist_ok=True)
            filepath = os.path.join(self._output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                for entry in data:
                    json_line = json.dumps(entry, ensure_ascii=False)
                    f.write(json_line + "\n")
        except IOError as e:
            print(f"ERROR: Failed to save JSONL file {filename}: {e}")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error while saving {filename}: {e}")
            raise
    
    def save_json(self, data: Dict, filename: str):
        """Save data in JSON format."""
        try:
            os.makedirs(self._output_dir, exist_ok=True)
            filepath = os.path.join(self._output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"ERROR: Failed to save JSON file {filename}: {e}")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error while saving {filename}: {e}")
            raise
    
    def _print_final_summary(
        self,
        toc_count: int,
        content_count: int,
        validation: Dict
    ):
        """Print comprehensive final summary."""
        page_stats = self._parser.get_page_coverage_stats()
        metrics = validation.get("detailed_metrics", {})
        
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"TOC Sections:        {toc_count:,}")
        print(f"Content Sections:    {content_count:,}")
        print(f"Total Pages:         {page_stats['total_pages']:,}")
        print(
            f"Pages Covered:       "
            f"{page_stats['pages_covered']:,}"
        )
        print(
            f"Page Coverage:       "
            f"{page_stats['coverage_percentage']}%"
        )
        print(f"\nQuality Metrics:")
        content_qual = metrics.get('content_quality_percentage', 0)
        print(f"  Content Quality:   {content_qual:.1f}%")
        overall = metrics.get('overall_quality_score', 0)
        print(f"  Overall Score:     {overall:.1f}%")
        print(f"\nValidation Status:   {validation['validation_status']}")
        print(f"Output Directory:    {self._output_dir}")
        print("="*60)
        print("✓ ALL FILES GENERATED SUCCESSFULLY!")
        print("="*60 + "\n")


if __name__ == "__main__":
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    pdf_path = os.path.join(
        project_root,
        "data",
        "input",
        "USB_PD_R3_2 V1.1 2024-10.pdf"
    )
    output_dir = os.path.join(project_root, "data", "output")
    
    app = USBPDParserApp(pdf_path, output_dir)
    app.run()