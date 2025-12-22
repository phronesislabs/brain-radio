"""Validator for function length rules."""

from typing import List

from tests.clean_code_validator.base import CodeNode, Validator
from tests.clean_code_validator.violations import Violation


class FunctionLengthValidator(Validator):
    """Validates function length rules (works for all languages)."""

    def __init__(self, max_lines: int = 20, warn_threshold: int = 15):
        """Initialize validator.

        Args:
            max_lines: Maximum allowed function lines
            warn_threshold: Threshold for warnings (before max)
        """
        self.max_lines = max_lines
        self.warn_threshold = warn_threshold

    @property
    def rule_name(self) -> str:
        """Return the name of the rule being validated."""
        return "function_length"

    def validate(self, node: CodeNode, source_lines: List[str]) -> List[Violation]:
        """Check if function exceeds max lines.

        Args:
            node: Code node to validate
            source_lines: Full source file lines

        Returns:
            List of violations found
        """
        violations = []

        if node.node_type != "function":
            return violations

        # Count non-comment, non-blank lines
        actual_lines = sum(
            1
            for line in source_lines[node.start_line - 1 : node.end_line]
            if line.strip() and not self._is_comment(line, node.language)
        )

        if actual_lines > self.max_lines:
            severity = "error"
            violations.append(
                Violation(
                    rule=self.rule_name,
                    file=node.file_path or "unknown",
                    line=node.start_line,
                    message=(
                        f"Function '{node.name}' has {actual_lines} lines (max: {self.max_lines})"
                    ),
                    severity=severity,
                    node_name=node.name,
                )
            )
        elif actual_lines > self.warn_threshold:
            severity = "warning"
            violations.append(
                Violation(
                    rule=self.rule_name,
                    file=node.file_path or "unknown",
                    line=node.start_line,
                    message=(
                        f"Function '{node.name}' has {actual_lines} lines "
                        f"(warning threshold: {self.warn_threshold})"
                    ),
                    severity=severity,
                    node_name=node.name,
                )
            )

        return violations
