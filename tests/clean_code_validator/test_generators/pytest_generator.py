"""Pytest test file generator."""

from pathlib import Path
from typing import Dict, List


class PytestGenerator:
    """Generates pytest test files for Clean Code validation."""

    def __init__(self, config: Dict):
        """Initialize generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def generate(self, output_path: Path) -> Path:
        """Generate pytest test file.

        Args:
            output_path: Path to output test file

        Returns:
            Path to generated test file
        """
        python_config = (
            self.config.get("project", {}).get("source_paths", {}).get("python", ["src"])
        )
        exclude_patterns = (
            self.config.get("project", {}).get("exclude_patterns", {}).get("python", [])
        )

        # Get rule configurations
        rules_config = self.config.get("rules", {})

        # Generate test file content
        content = self._generate_test_content(python_config, exclude_patterns, rules_config)

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def _generate_test_content(
        self, source_paths: List[str], exclude_patterns: List[str], rules_config: Dict
    ) -> str:
        """Generate test file content.

        Args:
            source_paths: List of source paths
            exclude_patterns: List of exclude patterns
            rules_config: Rule configurations

        Returns:
            Test file content as string
        """
        lines = [
            '"""Static Clean Code validation tests - Auto-generated from .cursor/rules/clean_code.mdc"""',
            "import pytest",
            "from pathlib import Path",
            "from tests.clean_code_validator.parsers.python_parser import PythonParser",
            "from tests.clean_code_validator.validators.function_length import FunctionLengthValidator",
            "from tests.clean_code_validator.validators.line_length import LineLengthValidator",
            "from tests.clean_code_validator.validators.naming_convention import NamingConventionValidator",
            "from tests.clean_code_validator.validators.parameter_count import ParameterCountValidator",
            "",
            "",
            "SOURCE_PATHS = " + repr(source_paths),
            "EXCLUDE_PATTERNS = " + repr(exclude_patterns),
            "",
            "",
            "def get_python_files():",
            '    """Get all Python files to validate."""',
            "    files = []",
            "    project_root = Path(__file__).parent.parent.parent",
            "    ",
            "    for source_path in SOURCE_PATHS:",
            "        source_dir = project_root / source_path",
            "        if source_dir.exists():",
            "            for py_file in source_dir.rglob('*.py'):",
            "                # Check exclude patterns",
            "                if any(",
            "                    pattern in str(py_file) for pattern in EXCLUDE_PATTERNS",
            "                ):",
            "                    continue",
            "                files.append(py_file)",
            "    ",
            "    return files",
            "",
            "",
            "class TestCleanCodeNames:",
            '    """Test naming conventions."""',
            "",
            "    def test_no_single_letter_names(self):",
            '        """Verify single-letter names only used for loop counters."""',
            "        parser = PythonParser()",
            "        validator = NamingConventionValidator()",
            "        violations = []",
            "        ",
            "        for file_path in get_python_files():",
            "            nodes = parser.parse_file(str(file_path))",
            "            source_lines = parser.get_source_lines(str(file_path))",
            "            ",
            "            for node in nodes:",
            "                node_violations = validator.validate(node, source_lines)",
            "                violations.extend(node_violations)",
            "        ",
            "        assert len(violations) == 0, (",
            "            f'Found {len(violations)} naming violations:\\n' +",
            "            '\\n'.join(str(v) for v in violations)",
            "        )",
            "",
            "",
            "class TestCleanCodeFunctions:",
            '    """Test function rules."""',
            "",
        ]

        # Add function length test
        if rules_config.get("function_length", {}).get("enabled", True):
            func_length_config = rules_config.get("function_length", {})
            max_lines = func_length_config.get("max_lines", 20)
            lines.extend(
                [
                    "    def test_function_length(self):",
                    f'        """Verify functions are small (max {max_lines} lines)."""',
                    "        parser = PythonParser()",
                    f"        validator = FunctionLengthValidator(max_lines={max_lines})",
                    "        violations = []",
                    "        ",
                    "        for file_path in get_python_files():",
                    "            nodes = parser.parse_file(str(file_path))",
                    "            source_lines = parser.get_source_lines(str(file_path))",
                    "            ",
                    "            for node in nodes:",
                    "                if node.node_type == 'function':",
                    "                    node_violations = validator.validate(node, source_lines)",
                    "                    violations.extend(node_violations)",
                    "        ",
                    "        assert len(violations) == 0, (",
                    "            f'Found {len(violations)} function length violations:\\n' +",
                    "            '\\n'.join(str(v) for v in violations)",
                    "        )",
                    "",
                ]
            )

        # Add parameter count test
        if rules_config.get("parameter_count", {}).get("enabled", True):
            param_config = rules_config.get("parameter_count", {})
            max_count = param_config.get("max_count", 3)
            lines.extend(
                [
                    "    def test_parameter_count(self):",
                    f'        """Verify functions have minimal parameters (max {max_count})."""',
                    "        parser = PythonParser()",
                    f"        validator = ParameterCountValidator(max_count={max_count})",
                    "        violations = []",
                    "        ",
                    "        for file_path in get_python_files():",
                    "            nodes = parser.parse_file(str(file_path))",
                    "            source_lines = parser.get_source_lines(str(file_path))",
                    "            ",
                    "            for node in nodes:",
                    "                if node.node_type == 'function':",
                    "                    node_violations = validator.validate(node, source_lines)",
                    "                    violations.extend(node_violations)",
                    "        ",
                    "        assert len(violations) == 0, (",
                    "            f'Found {len(violations)} parameter count violations:\\n' +",
                    "            '\\n'.join(str(v) for v in violations)",
                    "        )",
                    "",
                ]
            )

        # Add line length test
        if rules_config.get("line_length", {}).get("enabled", True):
            line_length_config = rules_config.get("line_length", {})
            max_chars = line_length_config.get("max_chars", 120)
            lines.extend(
                [
                    "class TestCleanCodeFormatting:",
                    '    """Test formatting rules."""',
                    "",
                    "    def test_line_length(self):",
                    f'        """Verify lines are not too long (max {max_chars} chars)."""',
                    "        parser = PythonParser()",
                    f"        validator = LineLengthValidator(max_chars={max_chars})",
                    "        violations = []",
                    "        ",
                    "        for file_path in get_python_files():",
                    "            nodes = parser.parse_file(str(file_path))",
                    "            source_lines = parser.get_source_lines(str(file_path))",
                    "            ",
                    "            for node in nodes:",
                    "                node_violations = validator.validate(node, source_lines)",
                    "                violations.extend(node_violations)",
                    "        ",
                    "        # Only fail on errors, not warnings",
                    "        errors = [v for v in violations if v.severity == 'error']",
                    "        assert len(errors) == 0, (",
                    "            f'Found {len(errors)} line length errors:\\n' +",
                    "            '\\n'.join(str(v) for v in errors)",
                    "        )",
                    "",
                ]
            )

        return "\n".join(lines)
