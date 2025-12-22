"""Project structure detection for Clean Code test generation."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class ProjectDetector:
    """Detects project structure, languages, and source paths."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector.

        Args:
            project_root: Project root directory. Defaults to current directory.
        """
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = Path(project_root)

    def detect_languages(self) -> List[str]:
        """Detect languages used in the project.

        Returns:
            List of detected language names
        """
        languages = []

        # Check for Python
        if (
            (self.project_root / "pyproject.toml").exists()
            or (self.project_root / "setup.py").exists()
            or (self.project_root / "requirements.txt").exists()
            or list(self.project_root.glob("**/*.py"))
        ):
            languages.append("python")

        # Check for TypeScript
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    package_data = json.load(f)
                    if "typescript" in str(package_data).lower():
                        languages.append("typescript")
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        if (
            (self.project_root / "tsconfig.json").exists()
            or list(self.project_root.glob("**/*.ts"))
            or list(self.project_root.glob("**/*.tsx"))
        ):
            languages.append("typescript")

        # Check for Rust
        if (self.project_root / "Cargo.toml").exists() or list(self.project_root.glob("**/*.rs")):
            languages.append("rust")

        # Check for shell scripts
        if list(self.project_root.glob("**/*.sh")) or list(self.project_root.glob("**/*.bash")):
            languages.append("shell")

        # Check for YAML (GitHub Actions, Terraform)
        if (
            (self.project_root / ".github" / "workflows").exists()
            or list(self.project_root.glob("**/*.yml"))
            or list(self.project_root.glob("**/*.yaml"))
        ):
            languages.append("yaml")

        return languages

    def detect_source_paths(self, language: str) -> List[str]:
        """Detect source paths for a specific language.

        Args:
            language: Language name

        Returns:
            List of source paths (relative to project root)
        """
        paths = []

        if language == "python":
            # Check pyproject.toml
            pyproject = self.project_root / "pyproject.toml"
            if pyproject.exists():
                try:
                    import tomli

                    with open(pyproject, "rb") as f:
                        data = tomli.load(f)
                        if "tool" in data and "setuptools" in data["tool"]:
                            packages = data["tool"]["setuptools"].get("packages", {})
                            if "find" in packages:
                                # Use common Python source directories
                                paths.extend(["src", "lib"])
                except (ImportError, KeyError, FileNotFoundError):
                    pass

            # Check setup.py
            setup_py = self.project_root / "setup.py"
            if setup_py.exists():
                # Common patterns
                paths.extend(["src", "lib"])

            # Default Python source paths
            if not paths:
                paths = ["src", "lib"]

        elif language == "typescript":
            # Check tsconfig.json
            tsconfig = self.project_root / "tsconfig.json"
            if tsconfig.exists():
                try:
                    with open(tsconfig, "r") as f:
                        data = json.load(f)
                        if "compilerOptions" in data:
                            root_dir = data["compilerOptions"].get("rootDir", "src")
                            paths.append(root_dir)
                except (json.JSONDecodeError, KeyError, FileNotFoundError):
                    pass

            # Check for frontend directory
            if (self.project_root / "frontend").exists():
                paths.append("frontend/src")

            # Default TypeScript source paths
            if not paths:
                paths = ["src", "frontend/src"]

        elif language == "rust":
            # Check Cargo.toml
            cargo_toml = self.project_root / "Cargo.toml"
            if cargo_toml.exists():
                paths.append("src")
            else:
                # Check for workspace
                for cargo_file in self.project_root.glob("**/Cargo.toml"):
                    rel_path = cargo_file.parent.relative_to(self.project_root)
                    if (rel_path / "src").exists():
                        paths.append(str(rel_path / "src"))

        elif language == "shell":
            # Common script directories
            for script_dir in ["scripts", "bin", "tools"]:
                if (self.project_root / script_dir).exists():
                    paths.append(script_dir)

        elif language == "yaml":
            # GitHub Actions workflows
            workflows_dir = self.project_root / ".github" / "workflows"
            if workflows_dir.exists():
                paths.append(".github/workflows")

            # Terraform
            terraform_dir = self.project_root / "terraform"
            if terraform_dir.exists():
                paths.append("terraform")

        return paths

    def detect_exclude_patterns(self, language: str) -> List[str]:
        """Detect exclude patterns for a language.

        Args:
            language: Language name

        Returns:
            List of exclude patterns
        """
        patterns = []

        if language == "python":
            patterns = [
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

        elif language == "typescript":
            patterns = [
                "node_modules",
                "dist",
                "build",
                "*.test.ts",
                "*.test.tsx",
                "*.spec.ts",
                "*.spec.tsx",
            ]

        elif language == "rust":
            patterns = ["target", "*.rs.bak"]

        elif language == "shell":
            patterns = ["*.sh.bak", "*.bash.bak"]

        elif language == "yaml":
            patterns = ["*.yml.bak", "*.yaml.bak"]

        return patterns

    def get_project_name(self) -> str:
        """Get project name from configuration files.

        Returns:
            Project name
        """
        # Try pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomli

                with open(pyproject, "rb") as f:
                    data = tomli.load(f)
                    if "project" in data and "name" in data["project"]:
                        return data["project"]["name"]
            except (ImportError, KeyError, FileNotFoundError):
                pass

        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    data = json.load(f)
                    if "name" in data:
                        return data["name"]
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Try Cargo.toml
        cargo_toml = self.project_root / "Cargo.toml"
        if cargo_toml.exists():
            try:
                with open(cargo_toml, "r") as f:
                    content = f.read()
                    match = re.search(r'name\s*=\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)
            except FileNotFoundError:
                pass

        # Default to directory name
        return self.project_root.name

    def generate_config(self) -> Dict:
        """Generate configuration dictionary.

        Returns:
            Configuration dictionary
        """
        languages = self.detect_languages()
        project_name = self.get_project_name()

        config = {
            "project": {
                "name": project_name,
                "languages": languages,
                "source_paths": {},
                "exclude_patterns": {},
            },
            "rules": {},
        }

        # Add source paths and exclude patterns for each language
        for language in languages:
            config["project"]["source_paths"][language] = self.detect_source_paths(language)
            config["project"]["exclude_patterns"][language] = self.detect_exclude_patterns(language)

        return config
