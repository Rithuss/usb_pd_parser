"""
Main Runner Script
Entry point demonstrating usage of Orchestrator.

OOP Concepts:
- Uses Factory Pattern
- Demonstrates Composition
- Shows Polymorphism in action
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import USBPDParserOrchestrator


def main():
    """
    Main entry point.
    
    Demonstrates:
    - Factory Pattern usage
    - Orchestrator pattern
    - Clean separation of concerns
    """
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
    
    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    
    pdf_path = (
        project_root / "data" / "input" /
        "USB_PD_R3_2 V1.1 2024-10.pdf"
    )
    
    output_dir = project_root / "data" / "output"
    
    # Check if PDF exists
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF file not found!")
        print(f"Expected location: {pdf_path}")
        print("\nPlease ensure the PDF is in the correct location.")
        return 1
    
    try:
        # Create orchestrator using COMPOSITION
        orchestrator = USBPDParserOrchestrator(
            str(pdf_path),
            str(output_dir)
        )
        
        # Execute complete pipeline
        orchestrator.execute()
        
        print("\n🎉 SUCCESS! All files generated successfully!")
        print(f"\nCheck output files in: {output_dir}")
        print("  📄 usb_pd_toc.jsonl")
        print("  📄 usb_pd_spec.jsonl")
        print("  📄 validation_report.json")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)