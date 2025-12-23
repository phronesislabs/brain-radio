"""Python-specific parser using AST module."""

import ast
from pathlib import Path
from typing import List

from tests.clean_code_validator.base import CodeNode, LanguageParser


class PythonParser(LanguageParser):
    """Python-specific parser using AST module."""

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse Python file and return CodeNode list.

        Args:
            file_path: Path to Python file

        Returns:
            List of CodeNode objects
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                tree = ast.parse(source, filename=file_path)
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            return []

        nodes = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get function parameters
                parameters = [arg.arg for arg in node.args.args]

                # Get source segment
                raw_source = None
                try:
                    if hasattr(ast, "get_source_segment"):
                        raw_source = ast.get_source_segment(source, node)
                except (AttributeError, ValueError):
                    pass

                # Determine end line
                end_line = node.end_lineno if hasattr(node, "end_lineno") else node.lineno

                nodes.append(
                    CodeNode(
                        node_type="function",
                        name=node.name,
                        start_line=node.lineno,
                        end_line=end_line,
                        parameters=parameters,
                        language="python",
                        raw_source=raw_source,
                        file_path=file_path,
                        metadata={
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "is_method": self._is_method(node, tree),
                        },
                    )
                )

            elif isinstance(node, ast.ClassDef):
                # Get source segment
                raw_source = None
                try:
                    if hasattr(ast, "get_source_segment"):
                        raw_source = ast.get_source_segment(source, node)
                except (AttributeError, ValueError):
                    pass

                # Determine end line
                end_line = node.end_lineno if hasattr(node, "end_lineno") else node.lineno

                nodes.append(
                    CodeNode(
                        node_type="class",
                        name=node.name,
                        start_line=node.lineno,
                        end_line=end_line,
                        parameters=[],
                        language="python",
                        raw_source=raw_source,
                        file_path=file_path,
                        metadata={
                            "bases": [self._unparse_base(base) for base in node.bases],
                        },
                    )
                )

        return nodes

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

    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is a method (defined inside a class).

        Args:
            node: Function node
            tree: AST tree

        Returns:
            True if function is a method
        """
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.walk(parent):
                    if child == node:
                        return True
        return False

    def _unparse_base(self, base: ast.expr) -> str:
        """Convert AST base class to string.

        Args:
            base: Base class AST node

        Returns:
            String representation
        """
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self._unparse_base(base.value)}.{base.attr}"
        else:
            try:
                return ast.unparse(base)
            except (AttributeError, ValueError):
                return str(base)
