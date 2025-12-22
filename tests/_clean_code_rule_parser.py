"""Parser for extracting Clean Code rules from markdown files."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RuleSection:
    """Represents a section of Clean Code rules."""

    title: str
    rules: List[Dict[str, str]] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    thresholds: Dict[str, any] = field(default_factory=dict)


@dataclass
class ParsedRules:
    """Structured representation of parsed Clean Code rules."""

    sections: List[RuleSection] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class CleanCodeRuleParser:
    """Parser for extracting rules from .cursor/rules/clean_code.mdc."""

    def __init__(self, rule_file: Optional[str] = None):
        """Initialize parser.

        Args:
            rule_file: Path to rule file. Defaults to .cursor/rules/clean_code.mdc
        """
        if rule_file is None:
            # Try to find the rule file relative to project root
            project_root = Path(__file__).parent.parent
            rule_file = project_root / ".cursor" / "rules" / "clean_code.mdc"
        self.rule_file = Path(rule_file)

    def parse(self) -> ParsedRules:
        """Parse the rule file and return structured rules.

        Returns:
            ParsedRules object with all extracted rules
        """
        if not self.rule_file.exists():
            raise FileNotFoundError(f"Rule file not found: {self.rule_file}")

        content = self.rule_file.read_text(encoding="utf-8")
        sections = self._extract_sections(content)
        metadata = self._extract_metadata(content)

        return ParsedRules(sections=sections, metadata=metadata)

    def _extract_sections(self, content: str) -> List[RuleSection]:
        """Extract rule sections from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of RuleSection objects
        """
        sections = []
        lines = content.split("\n")

        current_section: Optional[RuleSection] = None
        in_code_block = False
        code_block_language = ""
        code_block_content = []

        for i, line in enumerate(lines):
            # Check for section headers (##)
            if line.startswith("## ") and not in_code_block:
                # Save previous section
                if current_section:
                    sections.append(current_section)

                # Start new section
                title = line[3:].strip()
                current_section = RuleSection(title=title)

            # Check for code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    if current_section and code_block_content:
                        example = {
                            "language": code_block_language,
                            "code": "\n".join(code_block_content),
                        }
                        current_section.examples.append(example)
                    code_block_content = []
                    code_block_language = ""
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_block_language = line.strip()[3:].strip()
                continue

            if in_code_block:
                code_block_content.append(line)
                continue

            # Extract rules (bullet points with -)
            if current_section and line.strip().startswith("- **"):
                rule_text = line.strip()[2:].strip()  # Remove "- "
                # Extract rule name and description
                match = re.match(r"\*\*(.+?)\*\*", rule_text)
                if match:
                    rule_name = match.group(1)
                    description = rule_text[match.end() :].strip()
                    if description.startswith("-"):
                        description = description[1:].strip()

                    rule = {
                        "name": rule_name,
                        "description": description,
                        "line_number": i + 1,
                    }
                    current_section.rules.append(rule)

            # Extract thresholds and patterns from rules
            if current_section:
                self._extract_thresholds_from_line(line, current_section)

        # Add last section
        if current_section:
            sections.append(current_section)

        return sections

    def _extract_thresholds_from_line(self, line: str, section: RuleSection) -> None:
        """Extract numeric thresholds and patterns from a line.

        Args:
            line: Line to analyze
            section: Section to update with thresholds
        """
        # Look for common threshold patterns
        # Function length: "ideally < 20 lines"
        match = re.search(r"< (\d+) lines?", line, re.IGNORECASE)
        if match:
            section.thresholds["max_function_lines"] = int(match.group(1))

        # Line length: "< 120 characters"
        match = re.search(r"< (\d+) characters?", line, re.IGNORECASE)
        if match:
            section.thresholds["max_line_length"] = int(match.group(1))

        # Parameter count patterns
        match = re.search(r"(\d+) arguments?", line, re.IGNORECASE)
        if match and ("parameter" in line.lower() or "argument" in line.lower()):
            count = int(match.group(1))
            if "ideal" in line.lower() or "zero" in line.lower():
                section.thresholds["ideal_parameter_count"] = count
            elif "acceptable" in line.lower() or "good" in line.lower():
                section.thresholds["acceptable_parameter_count"] = count
            elif "avoid" in line.lower() or "should" in line.lower():
                section.thresholds["max_parameter_count"] = count

        # Naming patterns
        if "snake_case" in line:
            section.thresholds["naming_style"] = "snake_case"
        elif "camelCase" in line:
            section.thresholds["naming_style"] = "camelCase"
        elif "PascalCase" in line:
            section.thresholds["naming_style"] = "PascalCase"

    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from frontmatter.

        Args:
            content: Markdown content

        Returns:
            Dictionary of metadata
        """
        metadata = {}
        lines = content.split("\n")

        if lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")

        return metadata

    def get_rules_by_category(self, category: str) -> Optional[RuleSection]:
        """Get rules for a specific category.

        Args:
            category: Category name (e.g., "Functions", "Meaningful Names")

        Returns:
            RuleSection for the category, or None if not found
        """
        parsed = self.parse()
        for section in parsed.sections:
            if category.lower() in section.title.lower():
                return section
        return None

    def get_all_validators_config(self) -> Dict[str, Dict]:
        """Get configuration for all validators.

        Returns:
            Dictionary mapping validator names to their configurations
        """
        parsed = self.parse()
        config = {}

        for section in parsed.sections:
            section_lower = section.title.lower()

            # Function-related rules
            if "function" in section_lower:
                config["function_length"] = {
                    "enabled": True,
                    "max_lines": section.thresholds.get("max_function_lines", 20),
                    "warn_threshold": section.thresholds.get("max_function_lines", 20) - 5,
                }
                config["parameter_count"] = {
                    "enabled": True,
                    "ideal_count": section.thresholds.get("ideal_parameter_count", 0),
                    "acceptable_count": section.thresholds.get("acceptable_parameter_count", 2),
                    "max_count": section.thresholds.get("max_parameter_count", 3),
                }

            # Naming rules
            if "name" in section_lower:
                config["naming_convention"] = {
                    "enabled": True,
                    "noise_words": ["data", "info", "object", "variable"],
                    "allowed_single_letters": ["i", "j", "k"],
                }

            # Formatting rules
            if "formatting" in section_lower:
                config["line_length"] = {
                    "enabled": True,
                    "max_chars": section.thresholds.get("max_line_length", 120),
                    "hard_max": 200,
                }

        return config
