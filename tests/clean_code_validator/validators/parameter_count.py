"""Validator for function parameter count rules."""

from typing import List

from tests.clean_code_validator.base import CodeNode, Validator
from tests.clean_code_validator.violations import Violation


class ParameterCountValidator(Validator):
    """Validates function parameter count rules."""

    def __init__(
        self,
        ideal_count: int = 0,
        acceptable_count: int = 2,
        max_count: int = 3,
    ):
        """Initialize validator.

        Args:
            ideal_count: Ideal number of parameters (0 is best)
            acceptable_count: Acceptable number of parameters (2 is acceptable)
            max_count: Maximum before error (3 should be avoided)
        """
        self.ideal_count = ideal_count
        self.acceptable_count = acceptable_count
        self.max_count = max_count

    @property
    def rule_name(self) -> str:
        """Return the name of the rule being validated."""
        return "parameter_count"

    def validate(self, node: CodeNode, source_lines: List[str]) -> List[Violation]:
        """Check if function has too many parameters.

        Args:
            node: Code node to validate
            source_lines: Full source file lines

        Returns:
            List of violations found
        """
        violations = []

        if node.node_type != "function":
            return violations

        param_count = len(node.parameters)

        if param_count > self.max_count:
            violations.append(
                Violation(
                    rule=self.rule_name,
                    file=node.file_path or "unknown",
                    line=node.start_line,
                    message=(
                        f"Function '{node.name}' has {param_count} parameters "
                        f"(max: {self.max_count}). Consider using parameter objects."
                    ),
                    severity="error",
                    node_name=node.name,
                )
            )
        elif param_count > self.acceptable_count:
            violations.append(
                Violation(
                    rule=self.rule_name,
                    file=node.file_path or "unknown",
                    line=node.start_line,
                    message=(
                        f"Function '{node.name}' has {param_count} parameters "
                        f"(acceptable: {self.acceptable_count}). "
                        f"Consider reducing parameter count."
                    ),
                    severity="warning",
                    node_name=node.name,
                )
            )

        return violations
