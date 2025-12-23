"""Generate Clean Code test files and run them."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests._config_generator import ConfigGenerator  # noqa: E402
from tests._test_generator import TestGenerator  # noqa: E402


def main():
    """Generate config and test files, then run tests."""
    print("=" * 60)
    print("Generating Clean Code Test Files")
    print("=" * 60)

    # Generate configuration
    print("\n1. Generating configuration...")
    try:
        config_gen = ConfigGenerator(project_root=project_root)
        # Try to generate in tests directory instead of .cursor if that fails
        try:
            config_path = config_gen.generate()
            print(f"   [PASS] Generated config: {config_path}")
        except PermissionError:
            # If .cursor is restricted, generate in tests directory
            config_path = project_root / "tests" / "clean_code_test_config.yaml"
            config_gen.output_path = config_path
            config_path = config_gen.generate()
            print(f"   [PASS] Generated config: {config_path}")
    except Exception as e:
        print(f"   [FAIL] Failed to generate config: {e}")
        return 1

    # Generate test files
    print("\n2. Generating test files...")
    try:
        test_gen = TestGenerator(config_path=config_path)
        generated_files = test_gen.generate_all(output_dir=project_root / "tests")
        print(f"   [PASS] Generated {len(generated_files)} test file(s):")
        for file in generated_files:
            print(f"     - {file}")
    except Exception as e:
        print(f"   [FAIL] Failed to generate test files: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Run the generated tests
    print("\n3. Running generated tests...")
    try:
        import subprocess

        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_clean_code_static.py", "-v"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode == 0:
            print("   [PASS] All generated tests passed!")
        else:
            print(f"   [WARN] Some tests failed (exit code: {result.returncode})")
            return result.returncode
    except Exception as e:
        print(f"   [FAIL] Failed to run tests: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("[PASS] Generation and testing complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
