"""
Validation Report Writer
Writes validation reports in JSON format.

OOP Concepts:
- INHERITANCE: Inherits from BaseOutputWriter
- POLYMORPHISM: Different write() implementation
- ENCAPSULATION: Private formatting logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from core.base_classes import BaseOutputWriter


class ValidationReportWriter(BaseOutputWriter):
    """
    Validation report writer (JSON format).
    
    OOP Principles:
    - INHERITANCE: Extends BaseOutputWriter
    - POLYMORPHISM: Custom write() for reports
    - ENCAPSULATION: Private report formatting
    """
    
    def __init__(self, output_path: str):
        """
        Initialize validation report writer.
        
        Args:
            output_path: Path to output file
        """
        # INHERITANCE: Call parent
        super().__init__(output_path)
        
        # ENCAPSULATION: Private attributes
        self.__report_data = {}
        self.__generation_time = None
        self.__report_size = 0
        
        # ENCAPSULATION: Protected attributes
        self._format_name = "JSON"
        self._indent = 2  # Pretty-print JSON
    
    # PROPERTY: Access to private data
    @property
    def report_data(self) -> Dict:
        """Get report data (read-only)"""
        return self.__report_data.copy()
    
    @property
    def generation_time(self) -> str:
        """Get report generation time"""
        return (
            self.__generation_time.isoformat()
            if self.__generation_time else None
        )
    
    @property
    def report_size(self) -> int:
        """Get report size in bytes"""
        return self.__report_size
    
    # POLYMORPHISM: Override write method
    def write(self, data: Dict[str, Any]) -> bool:
        """
        Write validation report.
        
        POLYMORPHISM: Report-specific write logic.
        
        Args:
            data: Report data dictionary
            
        Returns:
            True if successful
        """
        try:
            # Enhance report with metadata
            enhanced_report = self.__enhance_report(data)
            
            # Ensure directory exists
            self.__ensure_directory()
            
            # Write JSON report
            with open(
                self.output_path,
                'w',
                encoding=self._encoding
            ) as f:
                json_str = json.dumps(
                    enhanced_report,
                    indent=self._indent,
                    ensure_ascii=self._ensure_ascii
                )
                f.write(json_str)
                
                self.__report_size = len(
                    json_str.encode('utf-8')
                )
            
            # Store data
            self.__report_data = enhanced_report
            self.__generation_time = datetime.now()
            
            # Mark as written
            self._mark_as_written(1)
            
            return True
            
        except Exception as e:
            print(f"Error writing report: {e}")
            return False
    
    # ENCAPSULATION: Private enhancer
    def __enhance_report(self, data: Dict) -> Dict:
        """
        Enhance report with metadata.
        
        Args:
            data: Base report data
            
        Returns:
            Enhanced report
        """
        enhanced = data.copy()
        
        # Add metadata if not present
        if "metadata" not in enhanced:
            enhanced["metadata"] = {}
        
        enhanced["metadata"]["generated_at"] = (
            datetime.now().isoformat()
        )
        enhanced["metadata"]["output_path"] = self.output_path
        enhanced["metadata"]["format"] = self._format_name
        
        return enhanced
    
    # ENCAPSULATION: Private helper
    def __ensure_directory(self):
        """Ensure output directory exists"""
        output_dir = Path(self.output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # PROTECTED METHOD: Get statistics
    def _get_report_stats(self) -> Dict:
        """
        Get report writing statistics.
        
        Returns:
            Statistics dictionary
        """
        base_stats = self._get_write_stats()
        report_stats = {
            "format": self._format_name,
            "report_size": self.__report_size,
            "generation_time": self.generation_time
        }
        
        return {**base_stats, **report_stats}
    
    # PUBLIC METHOD: Validate report structure
    def validate_report(self, data: Dict) -> bool:
        """
        Validate report structure before writing.
        
        Args:
            data: Report data to validate
            
        Returns:
            True if valid
        """
        required_keys = ["document", "summary", "validation_status"]
        
        return all(key in data for key in required_keys)
    
    # SPECIAL METHOD: Context manager
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """String representation"""
        return (
            f"ValidationReportWriter("
            f"path='{self.output_path}', "
            f"size={self.__report_size}B)"
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import WriterFactory
    WriterFactory.register_writer(
        "validation",
        ValidationReportWriter
    )