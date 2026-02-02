"""
Main Runner Script 
"""
import sys
import os
from pathlib import Path

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from orchestrator import USBPDParserOrchestrator


class BannerPrinter:
    """Handles printing of application banner."""
    
    @staticmethod
    def print_header():
        """Print application header."""
        print("\n" + "="*70)
        print(" USB POWER DELIVERY PARSER - COMPLETE OOP")
        print("="*70)
    
    @staticmethod
    def print_features():
        """Print OOP features."""
        features = [
            "✓ 3 Abstract Base Classes (ABC)",
            "✓ 7 Concrete Classes with Inheritance",
            "✓ Factory Pattern (3 factories)",
            "✓ Strategy Pattern (2 strategies)",
            "✓ Composition Pattern (Orchestrator)",
            "✓ 15+ Private Attributes",
            "✓ 10+ Protected Methods",
            "✓ 12+ Special Methods",
            "✓ 5+ Property Decorators"
        ]
        
        print("\nOOP Features Demonstrated:")
        for feature in features:
            print(f"  {feature}")
        print("="*70 + "\n")
    
    @staticmethod
    def print_success(output_dir: Path):
        """Print success message."""
        print("\n🎉 SUCCESS! All files generated successfully!")
        print(f"\nCheck output files in: {output_dir}")
        print("  📄 usb_pd_toc.jsonl")
        print("  📄 usb_pd_spec.jsonl")
        print("  📄 validation_report.json")


class PathValidator:
    """Validates file paths."""
    
    @staticmethod
    def get_paths() -> tuple:
        """Get project paths."""
        project_root = Path(__file__).parent.parent.parent
        pdf_path = (
            project_root / "data" / "input" /
            "USB_PD_R3_2 V1.1 2024-10.pdf"
        )
        output_dir = project_root / "data" / "output"
        
        return pdf_path, output_dir
    
    @staticmethod
    def validate_pdf(pdf_path: Path) -> bool:
        """Validate PDF exists."""
        if not pdf_path.exists():
            print(f"❌ ERROR: PDF file not found!")
            print(f"Expected location: {pdf_path}")
            print("\nPlease ensure the PDF is in correct location.")
            return False
        return True


class ApplicationRunner:
    """Runs the main application."""
    
    def __init__(self):
        self.banner = BannerPrinter()
        self.validator = PathValidator()
    
    def run(self) -> int:
        """Run the application."""
        self._print_initial_info()
        
        pdf_path, output_dir = self.validator.get_paths()
        
        if not self._validate_inputs(pdf_path):
            return 1
        
        return self._execute_parsing(pdf_path, output_dir)
    
    def _print_initial_info(self):
        """Print header and features."""
        self.banner.print_header()
        self.banner.print_features()
    
    def _validate_inputs(self, pdf_path: Path) -> bool:
        """Validate input files."""
        return self.validator.validate_pdf(pdf_path)
    
    def _execute_parsing(self, pdf_path: Path, output_dir: Path) -> int:
        """Execute parsing and handle results."""
        try:
            orchestrator = USBPDParserOrchestrator(
                str(pdf_path),
                str(output_dir)
            )
            orchestrator.execute()
            
            self.banner.print_success(output_dir)
            return 0
            
        except Exception as e:
            return self._handle_error(e)
    
    def _handle_error(self, error: Exception) -> int:
        """Handle execution error."""
        print(f"\n❌ ERROR: {str(error)}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    runner = ApplicationRunner()
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()