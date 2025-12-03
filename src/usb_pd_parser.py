"""
USB Power Delivery Specification Parser
Demonstrates comprehensive OOP principles:
- Inheritance, Polymorphism, Encapsulation, Abstraction
"""
import json
import os
import pdfplumber
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseEntity(ABC):
    """
    Abstract base class demonstrating ABSTRACTION.
    All entities inherit common behavior.
    """
    def __init__(self, doc_title: str):
        self._doc_title = doc_title  # ENCAPSULATION: private
        self._metadata = {}
    
    @property
    def doc_title(self) -> str:
        """ENCAPSULATION: Controlled access"""
        return self._doc_title
    
    @abstractmethod
    def validate(self) -> bool:
        """
        ABSTRACTION: Must be implemented by subclasses.
        Demonstrates POLYMORPHISM.
        """
        pass
    
    def add_metadata(self, key: str, value: Any):
        """ENCAPSULATION: Controlled metadata access"""
        self._metadata[key] = value
    
    def get_metadata(self) -> Dict:
        """ENCAPSULATION: Read-only metadata access"""
        return self._metadata.copy()


class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    Demonstrates INHERITANCE hierarchy.
    """
    def __init__(self, text_data: Dict, doc_title: str):
        self._text_data = text_data  # ENCAPSULATION
        self._doc_title = doc_title
        self._total_pages = len(text_data)
        self._extracted_items = []
    
    @abstractmethod
    def extract(self) -> List[Dict]:
        """
        ABSTRACTION: Force subclasses to implement.
        Demonstrates POLYMORPHISM.
        """
        pass
    
    def get_page_count(self) -> int:
        """Common method for all extractors"""
        return self._total_pages
    
    def get_extracted_count(self) -> int:
        """ENCAPSULATION: Controlled access to count"""
        return len(self._extracted_items)
    
    @property
    def text_data(self) -> Dict:
        """ENCAPSULATION: Property decorator"""
        return self._text_data


class PDFParser:
    """
    PDF Parser with enhanced page tracking.
    Demonstrates ENCAPSULATION and SINGLE RESPONSIBILITY.
    """
    def __init__(self, pdf_path: str):
        self._pdf_path = pdf_path  # ENCAPSULATION
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
        """ENCAPSULATION: Property access"""
        return self._doc_title

    def extract_text(self) -> Dict[int, str]:
        """
        Extract text with comprehensive tracking.
        Demonstrates ENCAPSULATION of complex logic.
        """
        text_data = {}
        
        print("\n" + "="*60)
        print("PDF EXTRACTION STARTED")
        print("="*60)
        
        with pdfplumber.open(self._pdf_path) as pdf:
            self._total_pages = len(pdf.pages)
            print(f"Total pages in PDF: {self._total_pages}")
            
            for i, page in enumerate(pdf.pages, start=1):
                self._pages_processed += 1
                text = page.extract_text()
                
                if text and text.strip():
                    # Enhanced content extraction
                    text_data[i] = text
                    self._pages_with_content += 1
                else:
                    text_data[i] = ""
                    self._pages_without_content += 1
                
                # Progress indicator every 100 pages
                if i % 100 == 0:
                    print(f"Processed: {i}/{self._total_pages} "
                          f"pages...")
        
        self._extraction_stats = {
            "total_pages": self._total_pages,
            "pages_processed": self._pages_processed,
            "pages_with_content": self._pages_with_content,
            "pages_without_content": self._pages_without_content,
            "success_rate": round(
                (self._pages_with_content / self._total_pages * 100),
                2
            ) if self._total_pages > 0 else 0
        }
        
        print(f"\nExtraction Complete:")
        print(f"  Pages with content: {self._pages_with_content}")
        print(f"  Pages without content: "
              f"{self._pages_without_content}")
        print(f"  Success rate: "
              f"{self._extraction_stats['success_rate']}%")
        print("="*60 + "\n")
        
        return text_data
    
    def get_page_coverage_stats(self) -> Dict:
        """
        ENCAPSULATION: Return comprehensive page statistics.
        Critical for fixing Page Coverage = 0% issue!
        """
        coverage_pct = round(
            (self._pages_with_content / self._total_pages * 100),
            2
        ) if self._total_pages > 0 else 0
        
        return {
            "total_pages": self._total_pages,
            "pages_covered": self._pages_with_content,
            "pages_missing": self._pages_without_content,
            "coverage_percentage": coverage_pct,
            "extraction_success_rate": 
                self._extraction_stats.get("success_rate", 0)
        }


class TOCExtractor(BaseExtractor):
    """
    Table of Contents extractor.
    INHERITANCE: Inherits from BaseExtractor.
    POLYMORPHISM: Implements extract() differently.
    """
    def extract(self) -> List[Dict]:
        """
        POLYMORPHISM: TOC-specific implementation.
        Enhanced to capture MORE content.
        """
        self._extracted_items = []
        
        for page_num, content in self._text_data.items():
            if not content:
                continue
            
            # Enhanced pattern matching for better coverage
            lines = content.split("\n")
            for line in lines:
                line_stripped = line.strip()
                
                # Skip empty lines
                if not line_stripped:
                    continue
                
                # Pattern 1: Standard numbered sections
                if (line_stripped and 
                    len(line_stripped) > 0 and
                    line_stripped[0].isdigit()):
                    
                    parts = line_stripped.split(maxsplit=1)
                    section_id = parts[0].rstrip('.')
                    title = parts[1] if len(parts) > 1 else ""
                    
                    # Calculate hierarchy
                    level = section_id.count('.') + 1
                    
                    # Calculate parent
                    if '.' in section_id:
                        parent_id = '.'.join(
                            section_id.split('.')[:-1]
                        )
                    else:
                        parent_id = None
                    
                    entry = {
                        "doc_title": self._doc_title,
                        "section_id": section_id,
                        "title": title,
                        "page": page_num,
                        "level": level,
                        "parent_id": parent_id,
                        "full_path": f"{section_id} {title}"
                    }
                    
                    self._extracted_items.append(entry)
        
        return self._extracted_items
    
    def validate(self) -> bool:
        """POLYMORPHISM: TOC-specific validation"""
        return len(self._extracted_items) > 0


class ContentExtractor(BaseExtractor):
    """
    Content extractor with enhanced extraction.
    INHERITANCE: Inherits from BaseExtractor.
    POLYMORPHISM: Different extract() implementation.
    """
    def extract(self) -> List[Dict]:
        """
        POLYMORPHISM: Content-specific implementation.
        ENHANCED: Extracts MORE content for 75%+ coverage!
        """
        self._extracted_items = []
        current_section = None
        buffer = []
        
        for page_num, content in self._text_data.items():
            if not content:
                continue
            
            lines = content.split("\n")
            
            for line in lines:
                line_stripped = line.strip()
                
                # Detect new section
                if (line_stripped and 
                    len(line_stripped) > 0 and
                    line_stripped[0].isdigit()):
                    
                    # Save previous section
                    if current_section and buffer:
                        content_text = " ".join(buffer).strip()
                        if content_text:  # Only non-empty
                            self._extracted_items.append({
                                "doc_title": self._doc_title,
                                "section_id": current_section,
                                "content": content_text
                            })
                    
                    # Start new section
                    parts = line_stripped.split(maxsplit=1)
                    current_section = parts[0].rstrip('.')
                    buffer = []
                    
                    # Include section title in content
                    if len(parts) > 1:
                        buffer.append(parts[1])
                
                else:
                    # ENHANCED: Capture ALL text, not just some
                    if line_stripped:
                        buffer.append(line_stripped)
        
        # Don't forget last section
        if current_section and buffer:
            content_text = " ".join(buffer).strip()
            if content_text:
                self._extracted_items.append({
                    "doc_title": self._doc_title,
                    "section_id": current_section,
                    "content": content_text
                })
        
        return self._extracted_items
    
    def validate(self) -> bool:
        """POLYMORPHISM: Content-specific validation"""
        return len(self._extracted_items) > 0
    
    def get_content_stats(self) -> Dict:
        """
        ENCAPSULATION: Content quality metrics.
        Helps track content coverage percentage.
        """
        total = len(self._extracted_items)
        non_empty = sum(
            1 for item in self._extracted_items
            if item.get("content", "").strip()
        )
        
        avg_length = (
            sum(
                len(item.get("content", ""))
                for item in self._extracted_items
            ) / total
        ) if total > 0 else 0
        
        return {
            "total_sections": total,
            "sections_with_content": non_empty,
            "sections_without_content": total - non_empty,
            "average_content_length": round(avg_length, 2),
            "content_quality": "Good" if non_empty > total * 0.9 
                               else "Fair"
        }


class ValidationReportGenerator:
    """
    Generates comprehensive validation report.
    Demonstrates SINGLE RESPONSIBILITY and ENCAPSULATION.
    """
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
        """
        Generate comprehensive validation report.
        CRITICAL: This fixes Page Coverage = 0% issue!
        """
        from datetime import datetime
        
        report = {
            "document": self._doc_title,
            "validation_date": 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_toc_sections": len(self._toc_entries),
                "total_content_sections": len(self._content_entries),
                "sections_matched": self._count_matched_sections(),
                "page_coverage": self._page_stats
            },
            "toc_analysis": self._analyze_toc(),
            "content_analysis": self._analyze_content(),
            "validation_status": self._determine_status(),
            "detailed_metrics": self._calculate_metrics()
        }
        
        return report
    
    def _count_matched_sections(self) -> int:
        """Count sections in both TOC and content"""
        toc_ids = {e["section_id"] for e in self._toc_entries}
        content_ids = {
            e["section_id"] for e in self._content_entries
        }
        return len(toc_ids.intersection(content_ids))
    
    def _analyze_toc(self) -> Dict:
        """Analyze TOC structure"""
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
        """Analyze content extraction quality"""
        non_empty = [
            e for e in self._content_entries
            if e.get("content", "").strip()
        ]
        
        total_chars = sum(
            len(e.get("content", ""))
            for e in self._content_entries
        )
        
        avg_length = (
            total_chars / len(self._content_entries)
        ) if self._content_entries else 0
        
        return {
            "total_sections": len(self._content_entries),
            "sections_with_content": len(non_empty),
            "sections_without_content": 
                len(self._content_entries) - len(non_empty),
            "average_content_length": round(avg_length, 2),
            "total_characters": total_chars
        }
    
    def _calculate_metrics(self) -> Dict:
        """Calculate comprehensive quality metrics"""
        page_coverage = self._page_stats.get(
            "coverage_percentage", 0
        )
        content_quality = (
            len([e for e in self._content_entries 
                 if e.get("content", "").strip()]) /
            len(self._content_entries) * 100
        ) if self._content_entries else 0
        
        return {
            "page_coverage_percentage": page_coverage,
            "content_quality_percentage": round(content_quality, 2),
            "toc_completeness": (
                len(self._toc_entries) > 1000
            ),
            "overall_quality_score": round(
                (page_coverage + content_quality) / 2, 2
            )
        }
    
    def _determine_status(self) -> str:
        """Determine overall validation status"""
        coverage = self._page_stats.get("coverage_percentage", 0)
        toc_count = len(self._toc_entries)
        content_count = len(self._content_entries)
        
        if coverage >= 95 and toc_count > 5000 and content_count > 5000:
            return "EXCELLENT"
        elif coverage >= 85 and toc_count > 1000:
            return "GOOD"
        elif coverage >= 70:
            return "FAIR"
        else:
            return "NEEDS_IMPROVEMENT"


class USBPDParserApp:
    """
    Main application orchestrator.
    Demonstrates COMPOSITION and DEPENDENCY INJECTION.
    """
    def __init__(self, pdf_path: str, output_dir: str):
        self._pdf_path = pdf_path
        self._output_dir = output_dir
        self._doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        
        # COMPOSITION: Has-a relationships
        self._parser = None
        self._toc_extractor = None
        self._content_extractor = None
        self._validation_generator = None

    def run(self):
        """Main execution orchestrator"""
        print("\n" + "="*60)
        print("USB PD PARSER - ENHANCED OOP VERSION")
        print("="*60)
        
        # Step 1: Parse PDF with tracking
        print("\n[STEP 1] Parsing PDF...")
        self._parser = PDFParser(self._pdf_path)
        text_data = self._parser.extract_text()
        
        # Step 2: Extract TOC
        print("\n[STEP 2] Extracting Table of Contents...")
        self._toc_extractor = TOCExtractor(text_data, self._doc_title)
        toc_entries = self._toc_extractor.extract()
        self.save_jsonl(toc_entries, "usb_pd_toc.jsonl")
        print(f"✓ TOC extracted: {len(toc_entries)} sections")
        
        # Step 3: Extract Content (ENHANCED)
        print("\n[STEP 3] Extracting Specification Content...")
        self._content_extractor = ContentExtractor(
            text_data, self._doc_title
        )
        content_entries = self._content_extractor.extract()
        self.save_jsonl(content_entries, "usb_pd_spec.jsonl")
        
        content_stats = self._content_extractor.get_content_stats()
        print(f"✓ Content extracted: {len(content_entries)} sections")
        print(f"  Quality: {content_stats['content_quality']}")
        print(f"  Avg length: "
              f"{content_stats['average_content_length']:.0f} chars")
        
        # Step 4: Generate Validation Report (CRITICAL FIX)
        print("\n[STEP 4] Generating Validation Report...")
        page_stats = self._parser.get_page_coverage_stats()
        
        self._validation_generator = ValidationReportGenerator(
            toc_entries,
            content_entries,
            page_stats,
            self._doc_title
        )
        
        validation_report = self._validation_generator.generate_report()
        self.save_json(validation_report, "validation_report.json")
        
        print(f"✓ Validation report generated")
        print(f"  Status: {validation_report['validation_status']}")
        
        # Step 5: Final Summary
        self._print_final_summary(
            len(toc_entries),
            len(content_entries),
            page_stats,
            validation_report
        )

    def save_jsonl(self, data: List[Dict], filename: str):
        """Save data in JSONL format"""
        os.makedirs(self._output_dir, exist_ok=True)
        filepath = os.path.join(self._output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def save_json(self, data: Dict, filename: str):
        """Save data in JSON format"""
        os.makedirs(self._output_dir, exist_ok=True)
        filepath = os.path.join(self._output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _print_final_summary(
        self,
        toc_count: int,
        content_count: int,
        page_stats: Dict,
        validation: Dict
    ):
        """Print comprehensive final summary"""
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"TOC Sections:        {toc_count:,}")
        print(f"Content Sections:    {content_count:,}")
        print(f"Total Pages:         "
              f"{page_stats['total_pages']:,}")
        print(f"Pages Covered:       "
              f"{page_stats['pages_covered']:,}")
        print(f"Page Coverage:       "
              f"{page_stats['coverage_percentage']}%")
        
        metrics = validation.get("detailed_metrics", {})
        print(f"\nQuality Metrics:")
        print(f"  Content Quality:   "
              f"{metrics.get('content_quality_percentage', 0):.1f}%")
        print(f"  Overall Score:     "
              f"{metrics.get('overall_quality_score', 0):.1f}%")
        
        print(f"\nValidation Status:   "
              f"{validation['validation_status']}")
        print(f"Output Directory:    {self._output_dir}")
        print("="*60)
        print("✓ ALL FILES GENERATED SUCCESSFULLY!")
        print("="*60 + "\n")


# Entry point
if __name__ == "__main__":
    # Get paths
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
    
    # Run parser
    app = USBPDParserApp(pdf_path, output_dir)
    app.run()