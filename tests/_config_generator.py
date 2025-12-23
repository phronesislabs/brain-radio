"""Configuration file generator for Clean Code tests."""

import yaml
from pathlib import Path

from tests._project_detector import ProjectDetector
from tests._clean_code_rule_parser import CleanCodeRuleParser


class ConfigGenerator:
    """Generates configuration file for Clean Code tests."""

    def __init__(self, project_root: Path = None, output_path: Path = None):
        """Initialize generator.

        Args:
            project_root: Project root directory
            output_path: Path to output config file
        """
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = Path(project_root)

        if output_path is None:
            output_path = self.project_root / ".cursor" / "clean_code_test_config.yaml"
        self.output_path = Path(output_path)

        self.detector = ProjectDetector(self.project_root)
        self.rule_parser = CleanCodeRuleParser()

    def generate(self) -> Path:
        """Generate configuration file.

        Returns:
            Path to generated config file
        """
        # Get project configuration
        config = self.detector.generate_config()

        # Get rule configurations
        rule_configs = self.rule_parser.get_all_validators_config()

        # Merge rule configs into main config
        config["rules"] = rule_configs

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write YAML file
        with open(self.output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return self.output_path
