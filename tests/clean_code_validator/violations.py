"""Violation data structures for rule violations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Violation:
    """Represents a Clean Code rule violation."""

    rule: str  # Rule name (e.g., "function_length", "naming_convention")
    file: str  # File path where violation occurred
    line: int  # Line number where violation occurred
    message: str  # Human-readable violation message
    severity: str = "error"  # 'error', 'warning', 'info'
    column: Optional[int] = None  # Optional column number
    node_name: Optional[str] = None  # Name of the code node (function, class, etc.)

    def __str__(self) -> str:
        """String representation of violation."""
        location = f"{self.file}:{self.line}"
        if self.column:
            location += f":{self.column}"
        return f"[{self.rule}] {location}: {self.message}"

    def to_dict(self) -> dict:
        """Convert violation to dictionary."""
        return {
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "severity": self.severity,
            "column": self.column,
            "node_name": self.node_name,
        }
