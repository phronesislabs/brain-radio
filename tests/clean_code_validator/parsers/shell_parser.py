"""Shell script parser (basic regex-based implementation)."""

import re
from pathlib import Path
from typing import List

from tests.clean_code_validator.base import CodeNode, LanguageParser


class ShellParser(LanguageParser):
    """Shell script parser using regex-based parsing."""

    # Pattern to match shell function definitions
    FUNCTION_PATTERN = re.compile(
        r"^\s*(function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\s*\{?", re.MULTILINE
    )

    def parse_file(self, file_path: str) -> List[CodeNode]:
        """Parse shell script file and return CodeNode list.

        Args:
            file_path: Path to shell script file

        Returns:
            List of CodeNode objects
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                source_lines = source.split("\n")
        except (UnicodeDecodeError, FileNotFoundError):
            return []

        nodes = []

        # Find function definitions
        for match in self.FUNCTION_PATTERN.finditer(source):
            func_name = match.group(2)
            start_line = source[: match.start()].count("\n") + 1

            # Try to find function end (next function or end of file)
            end_line = self._find_function_end(source_lines, start_line - 1)

            nodes.append(
                CodeNode(
                    node_type="function",
                    name=func_name,
                    start_line=start_line,
                    end_line=end_line,
                    parameters=[],  # Shell functions don't have typed parameters
                    language="shell",
                    raw_source=None,
                    file_path=file_path,
                    metadata={},
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

    def _find_function_end(self, source_lines: List[str], start_index: int) -> int:
        """Find the end line of a shell function.

        Args:
            source_lines: All source lines
            start_index: Starting line index (0-based)

        Returns:
            End line number (1-based)
        """
        brace_count = 0
        in_function = False

        for i in range(start_index, len(source_lines)):
            line = source_lines[i]

            # Count braces to find function end
            for char in line:
                if char == "{":
                    brace_count += 1
                    in_function = True
                elif char == "}":
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        return i + 1

            # If we find another function definition, this function has ended
            if i > start_index and self.FUNCTION_PATTERN.match(line.strip()):
                return i

        # If we can't find the end, return the last line
        return len(source_lines)
