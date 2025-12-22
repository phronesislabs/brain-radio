"""Test script to verify Clean Code validator system works."""

from pathlib import Path

from tests._project_detector import ProjectDetector
from tests._clean_code_rule_parser import CleanCodeRuleParser
from tests.clean_code_validator.parsers.python_parser import PythonParser
from tests.clean_code_validator.validators.function_length import FunctionLengthValidator
from tests.clean_code_validator.validators.line_length import LineLengthValidator
from tests.clean_code_validator.validators.naming_convention import NamingConventionValidator
from tests.clean_code_validator.validators.parameter_count import ParameterCountValidator


def test_project_detection():
    """Test project detection."""
    print("Testing project detection...")
    detector = ProjectDetector()
    languages = detector.detect_languages()
    print(f"  Detected languages: {languages}")
    assert "python" in languages, "Python should be detected"
    print("  [PASS] Project detection works")


def test_rule_parsing():
    """Test rule parsing."""
    print("\nTesting rule parsing...")
    parser = CleanCodeRuleParser()
    rules = parser.parse()
    print(f"  Parsed {len(rules.sections)} sections")
    assert len(rules.sections) > 0, "Should parse at least one section"

    config = parser.get_all_validators_config()
    print(f"  Validator config keys: {list(config.keys())}")
    assert "function_length" in config, "Should have function_length config"
    assert "line_length" in config, "Should have line_length config"
    print("  [PASS] Rule parsing works")


def test_python_parser():
    """Test Python parser."""
    print("\nTesting Python parser...")
    parser = PythonParser()
    test_file = Path(__file__).parent / "clean_code_validator" / "base.py"
    if test_file.exists():
        nodes = parser.parse_file(str(test_file))
        print(f"  Parsed {len(nodes)} nodes from base.py")
        assert len(nodes) > 0, "Should parse at least one node"
        for node in nodes[:3]:
            print(f"    - {node.node_type}: {node.name} (lines {node.start_line}-{node.end_line})")
        print("  [PASS] Python parser works")
    else:
        print("  [WARN] base.py not found, skipping parser test")


def test_validators():
    """Test validators."""
    print("\nTesting validators...")

    # Test with a simple code node
    from tests.clean_code_validator.base import CodeNode

    # Create a test function node
    test_node = CodeNode(
        node_type="function",
        name="test_function",
        start_line=1,
        end_line=25,  # Exceeds 20 line limit
        parameters=["arg1", "arg2", "arg3", "arg4"],  # Exceeds 3 param limit
        language="python",
        file_path="test.py",
    )

    source_lines = [f"    line {i}\n" for i in range(1, 26)]

    # Test function length validator
    func_validator = FunctionLengthValidator(max_lines=20)
    violations = func_validator.validate(test_node, source_lines)
    print(f"  Function length validator: {len(violations)} violations")
    assert len(violations) > 0, "Should find function length violation"

    # Test parameter count validator
    param_validator = ParameterCountValidator(max_count=3)
    violations = param_validator.validate(test_node, source_lines)
    print(f"  Parameter count validator: {len(violations)} violations")
    assert len(violations) > 0, "Should find parameter count violation"

    # Test line length validator
    long_line = "x" * 150 + "\n"
    test_node_short = CodeNode(
        node_type="function",
        name="test",
        start_line=1,
        end_line=1,
        language="python",
        file_path="test.py",
    )
    line_validator = LineLengthValidator(max_chars=120, hard_max=200)
    violations = line_validator.validate(test_node_short, [long_line])
    print(f"  Line length validator: {len(violations)} violations")
    assert len(violations) > 0, "Should find line length violation"

    # Test naming validator
    bad_name_node = CodeNode(
        node_type="function",
        name="x",  # Single letter, not allowed
        start_line=1,
        end_line=1,
        language="python",
        file_path="test.py",
    )
    naming_validator = NamingConventionValidator()
    violations = naming_validator.validate(bad_name_node, ["def x():\n"])
    print(f"  Naming validator: {len(violations)} violations")
    assert len(violations) > 0, "Should find naming violation"

    print("  [PASS] All validators work")


def test_end_to_end():
    """Test end-to-end: parse file, validate, find violations."""
    print("\nTesting end-to-end...")
    parser = PythonParser()
    test_file = Path(__file__).parent / "clean_code_validator" / "validators" / "function_length.py"

    if test_file.exists():
        nodes = parser.parse_file(str(test_file))
        source_lines = parser.get_source_lines(str(test_file))

        validator = FunctionLengthValidator(max_lines=20)
        all_violations = []

        for node in nodes:
            if node.node_type == "function":
                violations = validator.validate(node, source_lines)
                all_violations.extend(violations)

        print(f"  Found {len(all_violations)} violations in function_length.py")
        if all_violations:
            for v in all_violations[:3]:
                print(f"    - {v}")
        print("  [PASS] End-to-end test works")
    else:
        print("  [WARN] function_length.py not found, skipping end-to-end test")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Clean Code Validator System")
    print("=" * 60)

    try:
        test_project_detection()
        test_rule_parsing()
        test_python_parser()
        test_validators()
        test_end_to_end()

        print("\n" + "=" * 60)
        print("[PASS] All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
