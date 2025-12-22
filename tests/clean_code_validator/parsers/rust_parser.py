"""Rust-specific parser (stub for future implementation)."""

from typing import List

from tests.clean_code_validator.base import CodeNode, LanguageParser


class RustParser(LanguageParser):
    """Rust-specific parser (stub - requires tree-sitter-rust or syn crate bindings)."""

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse Rust file and return CodeNode list.

        Args:
            file_path: Path to Rust file

        Returns:
            List of CodeNode objects

        Note:
            This is a stub implementation. For full functionality, install:
            - tree-sitter-rust (via tree-sitter Python bindings)
            - or Python bindings to syn crate
        """
        # TODO: Implement with tree-sitter-rust or syn crate bindings
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
