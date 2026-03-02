"""JSONL writer utilities.

Write lists of dictionaries as JSON Lines (one JSON object per
line). Provides simple write/append operations and exposes write
statistics. Docstrings are concise and reflect the implemented
behavior.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List, Dict, Any
from pathlib import Path
from core.base_classes import BaseOutputWriter


class JSONLWriter(BaseOutputWriter):
    """Writer for JSON Lines (JSONL) format.

    Writes each dictionary as a compact JSON line. Tracks lines
    and bytes written and supports appending to existing files.
    """
    
    def __init__(self, output_path: str):
        """Initialize writer with the target output file path."""
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
        """Return the number of lines successfully written."""
        return self.__lines_written
    
    @property
    def bytes_written(self) -> int:
        """Return the total number of bytes written to the file."""
        return self.__bytes_written
    
    @property
    def format_name(self) -> str:
        """Return the output format name (JSONL)."""
        return self._format_name
    
    # POLYMORPHISM: Override abstract write method
    def write(self, data: List[Dict]) -> bool:
        """Overwrite the output file with `data` in JSONL format.

        Returns True on success; on failure the error is recorded
        and False is returned.
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
        """Create parent directories for the output file if missing."""
        output_dir = Path(self.output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # ENCAPSULATION: Private formatter
    def __format_json_line(self, data: Dict) -> str:
        """Serialize a dictionary to a JSON string for a single line."""
        return json.dumps(
            data,
            ensure_ascii=self._ensure_ascii,
            indent=self._indent
        )
    
    # PROTECTED METHOD: Get write statistics
    def _get_write_details(self) -> Dict:
        """Return detailed write statistics as a dictionary."""
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
        """Append entries to an existing JSONL file.

        Returns True on success; errors are recorded and False is
        returned on failure.
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
        """Return self to support usage as a context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit (no cleanup required)."""
        pass
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Return a short human-readable description of the writer."""
        return (
            f"JSONLWriter("
            f"path='{self.output_path}', "
            f"lines={self.__lines_written})"
        )


# Register with factory
if __name__ != "__main__":
    from core.factories import WriterFactory
    WriterFactory.register_writer("jsonl", JSONLWriter)