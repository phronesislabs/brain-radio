"""Main test generator that creates test files for all detected languages."""

import yaml
from pathlib import Path
from typing import List

from tests.clean_code_validator.test_generators.pytest_generator import PytestGenerator


class TestGenerator:
    """Main test generator for all languages."""

    def __init__(self, config_path: Path = None):
        """Initialize generator.

        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path.cwd() / ".cursor" / "clean_code_test_config.yaml"
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def generate_all(self, output_dir: Path = None) -> List[Path]:
        """Generate test files for all detected languages.

        Args:
            output_dir: Output directory for test files

        Returns:
            List of generated test file paths
        """
        if output_dir is None:
            output_dir = Path.cwd() / "tests"
        output_dir = Path(output_dir)

        generated_files = []
        languages = self.config.get("project", {}).get("languages", [])

        for language in languages:
            if language == "python":
                output_file = output_dir / "test_clean_code_static.py"
                generator = PytestGenerator(self.config)
                generated_files.append(generator.generate(output_file))

            # TODO: Add generators for other languages
            # elif language == "typescript":
            #     ...
            # elif language == "rust":
            #     ...

        return generated_files
