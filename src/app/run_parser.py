"""
Main Runner Script

Entry point for executing the USB PD Parser pipeline.
"""

import sys
from pathlib import Path

from orchestrator import USBPDParserOrchestrator


def print_banner() -> None:
    """Display application banner"""
    print("\n" + "=" * 70)
    print(" USB POWER DELIVERY PARSER")
    print(" COMPLETE OOP IMPLEMENTATION")
    print("=" * 70 + "\n")


def get_paths() -> tuple[Path, Path]:
    """Resolve project paths"""
    project_root = Path(__file__).resolve().parents[2]
    pdf_path = (
        project_root
        / "data"
        / "input"
        / "USB_PD_R3_2 V1.1 2024-10.pdf"
    )
    output_dir = project_root / "data" / "output"
    return pdf_path, output_dir


def pdf_exists(pdf_path: Path) -> bool:
    """Validate PDF availability"""
    if not pdf_path.exists():
        print("❌ PDF file not found")
        print(f"Expected path: {pdf_path}")
        return False
    return True


def run(pdf_path: Path, output_dir: Path) -> None:
    """Run parser orchestrator"""
    orchestrator = USBPDParserOrchestrator(
        str(pdf_path),
        str(output_dir),
    )
    orchestrator.execute()


def main() -> int:
    """Application entry point"""
    print_banner()

    pdf_path, output_dir = get_paths()

    if not pdf_exists(pdf_path):
        return 1

    try:
        run(pdf_path, output_dir)
        print("\n🎉 SUCCESS! Files generated successfully")
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print("\n❌ Execution failed")
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

