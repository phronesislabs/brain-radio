"""Static Clean Code validation tests - Auto-generated from .cursor/rules/clean_code.mdc"""

from pathlib import Path
from tests.clean_code_validator.parsers.python_parser import PythonParser
from tests.clean_code_validator.validators.function_length import FunctionLengthValidator
from tests.clean_code_validator.validators.line_length import LineLengthValidator
from tests.clean_code_validator.validators.naming_convention import NamingConventionValidator
from tests.clean_code_validator.validators.parameter_count import ParameterCountValidator


SOURCE_PATHS = ["src", "lib"]
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "*.egg-info",
    "dist",
    "build",
    "tests/",
    "test_*.py",
]


def get_python_files():
    """Get all Python files to validate."""
    files = []
    project_root = Path(__file__).parent.parent.parent

    for source_path in SOURCE_PATHS:
        source_dir = project_root / source_path
        if source_dir.exists():
            for py_file in source_dir.rglob("*.py"):
                # Check exclude patterns
                if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
                    continue
                files.append(py_file)

    return files


class TestCleanCodeNames:
    """Test naming conventions."""

    def test_no_single_letter_names(self):
        """Verify single-letter names only used for loop counters."""
        parser = PythonParser()
        validator = NamingConventionValidator()
        violations = []

        for file_path in get_python_files():
            nodes = parser.parse_file(str(file_path))
            source_lines = parser.get_source_lines(str(file_path))

            for node in nodes:
                node_violations = validator.validate(node, source_lines)
                violations.extend(node_violations)

        assert len(violations) == 0, f"Found {len(violations)} naming violations:\n" + "\n".join(
            str(v) for v in violations
        )


class TestCleanCodeFunctions:
    """Test function rules."""

    def test_function_length(self):
        """Verify functions are small (max 20 lines)."""
        parser = PythonParser()
        validator = FunctionLengthValidator(max_lines=20)
        violations = []

        for file_path in get_python_files():
            nodes = parser.parse_file(str(file_path))
            source_lines = parser.get_source_lines(str(file_path))

            for node in nodes:
                if node.node_type == "function":
                    node_violations = validator.validate(node, source_lines)
                    violations.extend(node_violations)

        assert len(violations) == 0, (
            f"Found {len(violations)} function length violations:\n"
            + "\n".join(str(v) for v in violations)
        )

    def test_parameter_count(self):
        """Verify functions have minimal parameters (max 3)."""
        parser = PythonParser()
        validator = ParameterCountValidator(max_count=3)
        violations = []

        for file_path in get_python_files():
            nodes = parser.parse_file(str(file_path))
            source_lines = parser.get_source_lines(str(file_path))

            for node in nodes:
                if node.node_type == "function":
                    node_violations = validator.validate(node, source_lines)
                    violations.extend(node_violations)

        assert len(violations) == 0, (
            f"Found {len(violations)} parameter count violations:\n"
            + "\n".join(str(v) for v in violations)
        )


class TestCleanCodeFormatting:
    """Test formatting rules."""

    def test_line_length(self):
        """Verify lines are not too long (max 120 chars)."""
        parser = PythonParser()
        validator = LineLengthValidator(max_chars=120)
        violations = []

        for file_path in get_python_files():
            nodes = parser.parse_file(str(file_path))
            source_lines = parser.get_source_lines(str(file_path))

            for node in nodes:
                node_violations = validator.validate(node, source_lines)
                violations.extend(node_violations)

        # Only fail on errors, not warnings
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0, f"Found {len(errors)} line length errors:\n" + "\n".join(
            str(v) for v in errors
        )
