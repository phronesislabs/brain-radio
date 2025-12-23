"""TypeScript-specific parser (stub for future implementation)."""

from typing import List

from tests.clean_code_validator.base import CodeNode, LanguageParser


class TypeScriptParser(LanguageParser):
    """TypeScript-specific parser (stub - requires tree-sitter or typescript-eslint-parser)."""

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse TypeScript file and return CodeNode list.

        Args:
            file_path: Path to TypeScript file

        Returns:
            List of CodeNode objects

        Note:
            This is a stub implementation. For full functionality, install:
            - tree-sitter-typescript (via tree-sitter Python bindings)
            - or typescript-eslint-parser
        """
        # TODO: Implement with tree-sitter-typescript or typescript-eslint-parser
        # For now, return empty list
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
