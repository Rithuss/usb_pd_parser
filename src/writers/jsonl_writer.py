"""
JSONL Writer
Writes data in JSONL format (one JSON per line).

OOP Concepts:
- INHERITANCE: Inherits from BaseOutputWriter
- POLYMORPHISM: Custom write() implementation
- ENCAPSULATION: Private file operations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List, Dict, Any
from pathlib import Path
from src.core.base_classes import BaseOutputWriter


class JSONLWriter(BaseOutputWriter):
    """
    JSONL format writer.
    
    OOP Principles:
    - INHERITANCE: Extends BaseOutputWriter
    - POLYMORPHISM: Custom write() implementation
    - ENCAPSULATION: Private write operations
    """
    
    def __init__(self, output_path: str):
        """
        Initialize JSONL writer.
        
        Args:
            output_path: Path to output file
        """
        # INHERITANCE: Call parent constructor
        super().__init__(output_path)
        
        # ENCAPSULATION: Private attributes
        self.__lines_written = 0
        self.__bytes_written = 0
        self.__write_errors = []
        
        # ENCAPSULATION: Protected attributes
        self._format_name = "JSONL"
        self._indent = None  # No indentation for JSONL
    
    # PROPERTY: Additional properties
    @property
    def lines_written(self) -> int:
        """Get number of lines written"""
        return self.__lines_written
    
    @property
    def bytes_written(self) -> int:
        """Get number of bytes written"""
        return self.__bytes_written
    
    @property
    def format_name(self) -> str:
        """Get format name"""
        return self._format_name
    
    # POLYMORPHISM: Override abstract write method
    def write(self, data: List[Dict]) -> bool:
        """
        Write data in JSONL format.
        
        POLYMORPHISM: JSONL-specific implementation.
        
        Args:
            data: List of dictionaries to write
            
        Returns:
            True if successful
        """
        try:
            # Ensure output directory exists
            self.__ensure_directory()
            
            # Write JSONL format
            with open(
                self.output_path,
                'w',
                encoding=self._encoding
            ) as f:
                for entry in data:
                    line = self.__format_json_line(entry)
                    f.write(line + '\n')
                    
                    self.__lines_written += 1
                    self.__bytes_written += len(line.encode('utf-8'))
            
            # Mark as written
            self._mark_as_written(len(data))
            
            return True
            
        except Exception as e:
            error_msg = f"Write error: {str(e)}"
            self.__write_errors.append(error_msg)
            return False
    
    # ENCAPSULATION: Private helper
    def __ensure_directory(self):
        """
        Ensure output directory exists.
        
        ENCAPSULATION: Private directory management.
        """
        output_dir = Path(self.output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # ENCAPSULATION: Private formatter
    def __format_json_line(self, data: Dict) -> str:
        """
        Format data as JSON line.
        
        Args:
            data: Dictionary to format
            
        Returns:
            JSON string
        """
        return json.dumps(
            data,
            ensure_ascii=self._ensure_ascii,
            indent=self._indent
        )
    
    # PROTECTED METHOD: Get write statistics
    def _get_write_details(self) -> Dict:
        """
        Get detailed write statistics.
        
        Returns:
            Statistics dictionary
        """
        base_stats = self._get_write_stats()
        jsonl_stats = {
            "format": self._format_name,
            "lines_written": self.__lines_written,
            "bytes_written": self.__bytes_written,
            "errors": len(self.__write_errors)
        }
        
        return {**base_stats, **jsonl_stats}
    
    # PUBLIC METHOD: Append to existing file
    def append(self, data: List[Dict]) -> bool:
        """
        Append data to existing JSONL file.
        
        Args:
            data: Data to append
            
        Returns:
            True if successful
        """
        try:
            with open(
                self.output_path,
                'a',
                encoding=self._encoding
            ) as f:
                for entry in data:
                    line = self.__format_json_line(entry)
                    f.write(line + '\n')
                    self.__lines_written += 1
            
            return True
            
        except Exception as e:
            self.__write_errors.append(str(e))
            return False
    
    # SPECIAL METHOD: Context manager support
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Could add cleanup here
        pass
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable representation"""
        return (
            f"JSONLWriter("
            f"path='{self.output_path}', "
            f"lines={self.__lines_written})"
        )

    
 