"""
Main Runner Script - REFACTORED
Fixed: main() from 64 lines to 10 lines
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import USBPDParserOrchestrator


def print_welcome_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print(" USB POWER DELIVERY PARSER - COMPLETE OOP IMPLEMENTATION")
    print("="*70)
    print("\nOOP Features Demonstrated:")
    print("  ✓ 3 Abstract Base Classes (ABC)")
    print("  ✓ 7 Concrete Classes with Inheritance")
    print("  ✓ Factory Pattern (3 factories)")
    print("  ✓ Strategy Pattern (2 strategies)")
    print("  ✓ Composition Pattern (Orchestrator)")
    print("  ✓ 15+ Private Attributes")
    print("  ✓ 10+ Protected Methods")
    print("  ✓ 12+ Special Methods")
    print("  ✓ 5+ Property Decorators")
    print("="*70 + "\n")


def get_project_paths():
    """Get PDF and output directory paths"""
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "input" / "USB_PD_R3_2 V1.1 2024-10.pdf"
    output_dir = project_root / "data" / "output"
    return pdf_path, output_dir


def validate_pdf_exists(pdf_path: Path) -> bool:
    """Check if PDF file exists"""
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF file not found!")
        print(f"Expected location: {pdf_path}")
        print("\nPlease ensure the PDF is in the correct location.")
        return False
    return True


def run_orchestrator(pdf_path: str, output_dir: str):
    """Execute the parser orchestrator"""
    orchestrator = USBPDParserOrchestrator(str(pdf_path), str(output_dir))
    orchestrator.execute()


def print_success_message(output_dir):
    """Print success message"""
    print("\n🎉 SUCCESS! All files generated successfully!")
    print(f"\nCheck output files in: {output_dir}")
    print("  📄 usb_pd_toc.jsonl")
    print("  📄 usb_pd_spec.jsonl")
    print("  📄 validation_report.json")
    print("  📄 execution_summary.json")


def main():
    """Main entry point"""
    print_welcome_banner()
    
    pdf_path, output_dir = get_project_paths()
    
    if not validate_pdf_exists(pdf_path):
        return 1
    
    try:
        run_orchestrator(pdf_path, output_dir)
        print_success_message(output_dir)
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)