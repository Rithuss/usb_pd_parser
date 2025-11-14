#!/usr/bin/env python3
"""
USB Power Delivery (PD) Parser Runner Script

This script manages the execution of both the USB PD parser
and the validation process using an object-oriented structure.
"""

import sys
import os
import argparse
import subprocess


class USBPDRunner:
    """
    Class to handle running the USB PD parser and validation.
    Demonstrates OOP principles: Encapsulation and
    Single Responsibility.
    """

    def __init__(self):
        """Initialize paths for parser and validation scripts."""
        self.base_dir = os.path.dirname(
            os.path.dirname(__file__)
        )
        self.app_dir = os.path.join(self.base_dir, "app")
        self.parser_script = os.path.join(
            self.base_dir,
            "usb_pd_parser.py"
        )
        self.check_script = os.path.join(
            os.path.dirname(self.base_dir),
            "tests",
            "check_sections.py"
        )

    def run_subprocess(self, script_path, working_dir):
        """
        Run a subprocess for a given script and handle output.
        
        Args:
            script_path: Path to the script to execute
            working_dir: Working directory for execution
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=working_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Warnings:", result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            script_name = os.path.basename(script_path)
            print(f"[ERROR] Script failed: {script_name}")
            print("Error output:", e.stderr)
            return False
        except FileNotFoundError:
            print(f"[ERROR] Script not found: {script_path}")
            return False

    def run_parser(self):
        """Run the USB PD parser."""
        print("[RUNNING] USB PD Parser...")
        print("-" * 40)
        return self.run_subprocess(
            self.parser_script,
            self.app_dir
        )

    def run_validation(self):
        """Run the section validation script."""
        print("\n[RUNNING] Section Validation...")
        print("-" * 40)
        return self.run_subprocess(
            self.check_script,
            self.base_dir
        )

    def execute(self, parse_only=False, check_only=False):
        """
        Execute parsing and/or validation based on user input.
        
        Args:
            parse_only: If True, only run parser
            check_only: If True, only run validation
            
        Returns:
            bool: True if all operations successful
        """
        success = True
        
        if check_only:
            success = self.run_validation()
        elif parse_only:
            success = self.run_parser()
        else:
            # Run both: parser first, then validation
            success = self.run_parser()
            if success:
                success = self.run_validation()
        
        return success


def main():
    """Main entry point for running the USB PD parser."""
    parser = argparse.ArgumentParser(
        description="USB PD Parser Runner"
    )
    parser.add_argument(
        "--parse-only",
        action="store_true",
        help="Run only the parser (skip validation)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run only the validation (skip parsing)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("USB Power Delivery Specification Parser")
    print("=" * 60)

    runner = USBPDRunner()
    success = runner.execute(
        parse_only=args.parse_only,
        check_only=args.check_only
    )

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] All operations completed successfully!")
    else:
        print("[ERROR] Some operations failed. "
              "Check the output above.")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())