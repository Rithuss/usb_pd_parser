import json
import os
import pdfplumber
from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """
    Abstract base class for extractors demonstrating INHERITANCE.
    Provides common functionality for all extractor types.
    """
    def __init__(self, text_data, doc_title):
        self.text_data = text_data
        self.doc_title = doc_title
        self.total_pages = len(text_data)
    
    @abstractmethod
    def extract(self):
        """
        Abstract method - must be implemented by subclasses.
        Demonstrates POLYMORPHISM.
        """
        pass
    
    def get_page_count(self):
        """Common method for all extractors"""
        return self.total_pages


class PDFParser:
    """
    PDF Parser class demonstrating ENCAPSULATION.
    Handles PDF file reading and text extraction.
    """
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        self.total_pages_in_pdf = 0
        self.pages_with_content = 0
        self.pages_without_content = 0

    def extract_text(self):
        """
        Extract text page by page using pdfplumber.
        Tracks page coverage for validation.
        """
        text_data = {}
        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages_in_pdf = len(pdf.pages)
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    text_data[i] = text
                    self.pages_with_content += 1
                else:
                    text_data[i] = ""
                    self.pages_without_content += 1
                    print(f"Warning: Page {i} has no text!")
        
        print(f"\n[PDF Parser] Total pages in PDF: "
              f"{self.total_pages_in_pdf}")
        print(f"[PDF Parser] Pages with content: "
              f"{self.pages_with_content}")
        print(f"[PDF Parser] Pages without content: "
              f"{self.pages_without_content}")
        
        return text_data
    
    def get_page_coverage_stats(self):
        """
        Return page coverage statistics for validation report.
        """
        coverage_percentage = (
            (self.pages_with_content / self.total_pages_in_pdf * 100)
            if self.total_pages_in_pdf > 0 else 0
        )
        return {
            "total_pages": self.total_pages_in_pdf,
            "pages_covered": self.pages_with_content,
            "pages_missing": self.pages_without_content,
            "coverage_percentage": round(coverage_percentage, 2)
        }


class TOCExtractor(BaseExtractor):
    """
    Table of Contents extractor demonstrating INHERITANCE.
    Inherits from BaseExtractor and implements extract() method.
    """
    def extract(self):
        """
        Extract TOC entries - implements abstract method.
        Demonstrates POLYMORPHISM.
        """
        toc_entries = []
        for page_num, content in self.text_data.items():
            if not content:
                continue
            for line in content.split("\n"):
                line_stripped = line.strip()
                if line_stripped and line_stripped[0].isdigit():
                    parts = line_stripped.split(" ", 1)
                    section_id = parts[0]
                    title = parts[1] if len(parts) > 1 else ""
                    
                    # Calculate hierarchy level
                    level = len(section_id.split("."))
                    
                    # Calculate parent_id
                    parent_id = (
                        ".".join(section_id.split(".")[:-1])
                        if "." in section_id else None
                    )
                    
                    toc_entries.append({
                        "doc_title": self.doc_title,
                        "section_id": section_id,
                        "title": title,
                        "page": page_num,
                        "level": level,
                        "parent_id": parent_id,
                        "full_path": f"{section_id} {title}"
                    })
        return toc_entries


class ContentExtractor(BaseExtractor):
    """
    Content extractor demonstrating INHERITANCE.
    Inherits from BaseExtractor and implements extract() method.
    """
    def extract(self):
        """
        Extract section content - implements abstract method.
        Demonstrates POLYMORPHISM.
        """
        contents = []
        current_section = None
        buffer = []

        for page_num, content in self.text_data.items():
            if not content:
                continue
            for line in content.split("\n"):
                line_stripped = line.strip()
                if line_stripped and line_stripped[0].isdigit():
                    if current_section:
                        contents.append({
                            "doc_title": self.doc_title,
                            "section_id": current_section,
                            "content": " ".join(buffer).strip()
                        })
                        buffer = []
                    current_section = line_stripped.split(" ", 1)[0]
                else:
                    buffer.append(line_stripped)

        if current_section and buffer:
            contents.append({
                "doc_title": self.doc_title,
                "section_id": current_section,
                "content": " ".join(buffer).strip()
            })
        return contents


class ValidationReportGenerator:
    """
    Generates validation report in VLS format.
    Demonstrates SINGLE RESPONSIBILITY PRINCIPLE.
    """
    def __init__(
        self,
        toc_entries,
        content_entries,
        page_stats,
        doc_title
    ):
        self.toc_entries = toc_entries
        self.content_entries = content_entries
        self.page_stats = page_stats
        self.doc_title = doc_title
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        report = {
            "document": self.doc_title,
            "validation_date": self._get_current_date(),
            "summary": {
                "total_toc_sections": len(self.toc_entries),
                "total_content_sections": len(self.content_entries),
                "sections_matched": self._count_matched_sections(),
                "page_coverage": self.page_stats
            },
            "toc_analysis": self._analyze_toc(),
            "content_analysis": self._analyze_content(),
            "validation_status": self._determine_status()
        }
        return report
    
    def _get_current_date(self):
        """Get current date for report"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _count_matched_sections(self):
        """Count sections that appear in both TOC and content"""
        toc_ids = {entry["section_id"] for entry in self.toc_entries}
        content_ids = {
            entry["section_id"] for entry in self.content_entries
        }
        matched = toc_ids.intersection(content_ids)
        return len(matched)
    
    def _analyze_toc(self):
        """Analyze TOC structure"""
        levels = {}
        for entry in self.toc_entries:
            level = entry["level"]
            levels[level] = levels.get(level, 0) + 1
        
        return {
            "total_sections": len(self.toc_entries),
            "hierarchy_levels": len(levels),
            "sections_per_level": levels
        }
    
    def _analyze_content(self):
        """Analyze content extraction"""
        non_empty_content = [
            e for e in self.content_entries
            if e["content"].strip()
        ]
        
        return {
            "total_sections": len(self.content_entries),
            "sections_with_content": len(non_empty_content),
            "sections_without_content": (
                len(self.content_entries) - len(non_empty_content)
            )
        }
    
    def _determine_status(self):
        """Determine overall validation status"""
        coverage = self.page_stats["coverage_percentage"]
        toc_count = len(self.toc_entries)
        content_count = len(self.content_entries)
        
        if coverage >= 95 and toc_count > 0 and content_count > 0:
            return "PASS"
        elif coverage >= 80:
            return "PARTIAL"
        else:
            return "FAIL"


class USBPDParserApp:
    """
    Main application class demonstrating COMPOSITION.
    Orchestrates all components to produce outputs.
    """
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.doc_title = (
            "USB Power Delivery Specification, "
            "Revision 3.2, Version 1.1, 2024-10"
        )
        self.parser = None
        self.toc_extractor = None
        self.content_extractor = None
        self.validation_generator = None

    def run(self):
        """Main execution method"""
        print("="*60)
        print("USB PD Parser - Starting Extraction")
        print("="*60)
        
        # Step 1: Parse PDF
        self.parser = PDFParser(self.pdf_path)
        text_data = self.parser.extract_text()
        
        # Step 2: Extract TOC
        print("\n[Extracting] Table of Contents...")
        self.toc_extractor = TOCExtractor(text_data, self.doc_title)
        toc_entries = self.toc_extractor.extract()
        self.save_jsonl(toc_entries, "usb_pd_toc.jsonl")
        print(f"[Success] TOC extracted: {len(toc_entries)} sections")
        
        # Step 3: Extract Content
        print("\n[Extracting] Specification Content...")
        self.content_extractor = ContentExtractor(
            text_data,
            self.doc_title
        )
        content_entries = self.content_extractor.extract()
        self.save_jsonl(content_entries, "usb_pd_spec.jsonl")
        print(f"[Success] Content extracted: "
              f"{len(content_entries)} sections")
        
        # Step 4: Generate Validation Report
        print("\n[Generating] Validation Report...")
        page_stats = self.parser.get_page_coverage_stats()
        self.validation_generator = ValidationReportGenerator(
            toc_entries,
            content_entries,
            page_stats,
            self.doc_title
        )
        validation_report = self.validation_generator.generate_report()
        self.save_json(validation_report, "validation_report.json")
        print("[Success] Validation report generated")
        
        # Step 5: Summary
        self._print_summary(
            len(toc_entries),
            len(content_entries),
            page_stats
        )

    def save_jsonl(self, data, filename):
        """Save data in JSONL format"""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")
    
    def save_json(self, data, filename):
        """Save data in JSON format"""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _print_summary(self, toc_count, content_count, page_stats):
        """Print execution summary"""
        print("\n" + "="*60)
        print("USB PD Parser - Execution Summary")
        print("="*60)
        print(f"TOC Sections:      {toc_count}")
        print(f"Content Sections:  {content_count}")
        print(f"Total Pages:       {page_stats['total_pages']}")
        print(f"Pages Covered:     {page_stats['pages_covered']}")
        print(f"Coverage:          "
              f"{page_stats['coverage_percentage']}%")
        print(f"\nOutput Directory:  {self.output_dir}")
        print("="*60)
        print("[SUCCESS] All files generated successfully!")
        print("="*60)


# Entry point
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