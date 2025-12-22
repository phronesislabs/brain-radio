"""Validator for naming convention rules."""

import re
from typing import List

from tests.clean_code_validator.base import CodeNode, Validator
from tests.clean_code_validator.violations import Violation


class NamingConventionValidator(Validator):
    """Validates naming convention rules (language-specific patterns)."""

    def __init__(
        self,
        noise_words: List[str] = None,
        allowed_single_letters: List[str] = None,
    ):
        """Initialize validator.

        Args:
            noise_words: Words that should be avoided (data, info, object, etc.)
            allowed_single_letters: Single letters allowed (i, j, k for loops)
        """
        self.noise_words = noise_words or ["data", "info", "object", "variable"]
        self.allowed_single_letters = allowed_single_letters or ["i", "j", "k"]

        # Language-specific naming patterns
        self.patterns = {
            "python": {
                "class": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),  # PascalCase
                "function": re.compile(r"^[a-z][a-z0-9_]*$"),  # snake_case
                "variable": re.compile(r"^[a-z][a-z0-9_]*$"),  # snake_case
            },
            "typescript": {
                "class": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),  # PascalCase
                "function": re.compile(r"^[a-z][a-zA-Z0-9]*$"),  # camelCase
                "variable": re.compile(r"^[a-z][a-zA-Z0-9]*$"),  # camelCase
            },
            "rust": {
                "struct": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),  # PascalCase
                "function": re.compile(r"^[a-z][a-z0-9_]*$"),  # snake_case
                "variable": re.compile(r"^[a-z][a-z0-9_]*$"),  # snake_case
            },
            "shell": {
                "function": re.compile(r"^[a-z][a-z0-9_]*$"),  # lowercase_with_underscores
                "variable": re.compile(r"^[A-Z_][A-Z0-9_]*$"),  # UPPER_CASE for constants
            },
        }

    @property
    def rule_name(self) -> str:
        """Return the name of the rule being validated."""
        return "naming_convention"

    def validate(self, node: CodeNode, source_lines: List[str]) -> List[Violation]:
        """Check naming conventions.

        Args:
            node: Code node to validate
            source_lines: Full source file lines

        Returns:
            List of violations found
        """
        violations = []

        # Check single-letter names
        if len(node.name) == 1:
            if node.name.lower() not in self.allowed_single_letters:
                violations.append(
                    Violation(
                        rule=self.rule_name,
                        file=node.file_path or "unknown",
                        line=node.start_line,
                        message=(
                            f"Single-letter name '{node.name}' should only be used "
                            f"for loop counters ({', '.join(self.allowed_single_letters)})"
                        ),
                        severity="error",
                        node_name=node.name,
                    )
                )

        # Check noise words
        name_lower = node.name.lower()
        for noise_word in self.noise_words:
            if noise_word in name_lower:
                violations.append(
                    Violation(
                        rule=self.rule_name,
                        file=node.file_path or "unknown",
                        line=node.start_line,
                        message=(f"Name '{node.name}' contains noise word '{noise_word}'"),
                        severity="warning",
                        node_name=node.name,
                    )
                )

        # Check naming patterns (language-specific)
        language_patterns = self.patterns.get(node.language, {})
        node_type_key = node.node_type

        # Map node types to pattern keys
        if node_type_key == "class" and "class" in language_patterns:
            pattern = language_patterns["class"]
            expected_format = "PascalCase"
        elif node_type_key == "struct" and "struct" in language_patterns:
            pattern = language_patterns["struct"]
            expected_format = "PascalCase"
        elif node_type_key == "function" and "function" in language_patterns:
            pattern = language_patterns["function"]
            if node.language == "python" or node.language == "rust":
                expected_format = "snake_case"
            elif node.language == "typescript":
                expected_format = "camelCase"
            else:
                expected_format = "lowercase_with_underscores"
        elif node_type_key == "variable" and "variable" in language_patterns:
            pattern = language_patterns["variable"]
            if node.language == "python" or node.language == "rust":
                expected_format = "snake_case"
            elif node.language == "typescript":
                expected_format = "camelCase"
            else:
                expected_format = "UPPER_CASE"
        else:
            # No pattern defined for this node type/language combination
            return violations

        if not pattern.match(node.name):
            violations.append(
                Violation(
                    rule=self.rule_name,
                    file=node.file_path or "unknown",
                    line=node.start_line,
                    message=(
                        f"{node.node_type.capitalize()} '{node.name}' does not follow "
                        f"{expected_format} naming convention"
                    ),
                    severity="error",
                    node_name=node.name,
                )
            )

        return violations
