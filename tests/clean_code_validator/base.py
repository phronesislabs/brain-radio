"""Abstract base classes for language-agnostic code validation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Protocol, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tests.clean_code_validator.violations import Violation


@dataclass
class CodeNode:
    """Language-agnostic representation of code constructs."""

    node_type: str  # 'function', 'class', 'variable', etc.
    name: str
    start_line: int
    end_line: int
    parameters: List[str] = field(default_factory=list)  # For functions/methods
    language: str = "python"  # 'python', 'typescript', 'rust', etc.
    raw_source: Optional[str] = None  # Original source code
    file_path: Optional[str] = None  # Path to source file
    metadata: dict = field(default_factory=dict)  # Language-specific metadata


class LanguageParser(Protocol):
    """Protocol for language-specific parsers."""

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse a file and return code nodes."""
        ...

    def get_source_lines(self, file_path: str) -> List[str]:
        """Get source lines for a file."""
        ...


class Validator(ABC):
    """Abstract base class for rule validators."""

    @abstractmethod
    def validate(self, node: CodeNode, source_lines: List[str]) -> List["Violation"]:  # noqa: F821
        """Validate a code node against the rule.

        Args:
            node: The code node to validate
            source_lines: Full source file lines for context

        Returns:
            List of violations found
        """
        ...

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the name of the rule being validated."""
        ...

    def _is_comment(self, line: str, language: str) -> bool:
        """Check if a line is a comment (language-specific).

        Args:
            line: Source line to check
            language: Programming language

        Returns:
            True if line is a comment
        """
        stripped = line.strip()
        if language == "python":
            return stripped.startswith("#")
        elif language in ["typescript", "javascript", "rust"]:
            return stripped.startswith("//") or stripped.startswith("/*")
        elif language == "shell":
            return stripped.startswith("#")
        return False
