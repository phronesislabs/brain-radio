"""Validator for line length rules."""

from typing import List

from tests.clean_code_validator.base import CodeNode, Validator
from tests.clean_code_validator.violations import Violation


class LineLengthValidator(Validator):
    """Validates line length rules (universal for all languages)."""

    def __init__(self, max_chars: int = 120, hard_max: int = 200):
        """Initialize validator.

        Args:
            max_chars: Preferred maximum line length
            hard_max: Hard maximum (always an error)
        """
        self.max_chars = max_chars
        self.hard_max = hard_max

    @property
    def rule_name(self) -> str:
        """Return the name of the rule being validated."""
        return "line_length"

    def validate(self, node: CodeNode, source_lines: List[str]) -> List[Violation]:
        """Check if any lines exceed max length.

        Args:
            node: Code node to validate (can be any node type)
            source_lines: Full source file lines

        Returns:
            List of violations found
        """
        violations = []

        # Check all lines in the node's range
        for line_num in range(node.start_line, node.end_line + 1):
            if line_num > len(source_lines):
                continue

            line = source_lines[line_num - 1]
            line_length = len(line.rstrip("\n\r"))

            # Skip comments for warnings, but still check hard max
            is_comment = self._is_comment(line, node.language)

            if line_length > self.hard_max:
                # Hard max is always an error
                violations.append(
                    Violation(
                        rule=self.rule_name,
                        file=node.file_path or "unknown",
                        line=line_num,
                        message=(
                            f"Line {line_num} has {line_length} characters "
                            f"(hard max: {self.hard_max})"
                        ),
                        severity="error",
                        column=self.max_chars + 1,
                    )
                )
            elif line_length > self.max_chars and not is_comment:
                # Exceeding preferred max is a warning (unless it's a comment)
                violations.append(
                    Violation(
                        rule=self.rule_name,
                        file=node.file_path or "unknown",
                        line=line_num,
                        message=(
                            f"Line {line_num} has {line_length} characters "
                            f"(preferred max: {self.max_chars})"
                        ),
                        severity="warning",
                        column=self.max_chars + 1,
                    )
                )

        return violations
