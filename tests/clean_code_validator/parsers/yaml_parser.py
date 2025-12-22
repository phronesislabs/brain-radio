"""YAML parser for GitHub Actions and Terraform configs."""

from pathlib import Path
from typing import List

from tests.clean_code_validator.base import CodeNode, LanguageParser


class YAMLParser(LanguageParser):
    """YAML parser for configuration files (GitHub Actions, Terraform, etc.)."""

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse YAML file and return CodeNode list.

        Args:
            file_path: Path to YAML file

        Returns:
            List of CodeNode objects

        Note:
            YAML files are treated as configuration, not code with functions/classes.
            This parser creates a single "file" node for line length validation.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_lines = f.readlines()
        except (UnicodeDecodeError, FileNotFoundError):
            return []

        # For YAML files, create a single node representing the entire file
        # This allows line length validation
        if source_lines:
            return [
                CodeNode(
                    node_type="file",
                    name=file_path_obj.name,
                    start_line=1,
                    end_line=len(source_lines),
                    parameters=[],
                    language="yaml",
                    raw_source=None,
                    file_path=file_path,
                    metadata={"file_type": self._detect_file_type(file_path)},
                )
            ]

        return []

    def get_source_lines(self, file_path: str) -> List[str]:
        """Get source lines for a file.

        Args:
            file_path: Path to file

        Returns:
            List of source lines
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except (UnicodeDecodeError, FileNotFoundError):
            return []

    def _detect_file_type(self, file_path: str) -> str:
        """Detect the type of YAML file (GitHub Actions, Terraform, etc.).

        Args:
            file_path: Path to YAML file

        Returns:
            File type string
        """
        path_str = str(file_path)
        if ".github/workflows" in path_str:
            return "github_actions"
        elif "terraform" in path_str.lower() or path_str.endswith(".tf"):
            return "terraform"
        else:
            return "yaml"
