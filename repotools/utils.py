import ast
from typing import List


class Utils:
    def __init__(self, lang: str):
        self._lang: str = lang

    def lang(self) -> str:
        return self._lang

    def get_language_extensions(self) -> List[str]:
        language_extensions = {
                "python": [".py", ".pyw"],
                "go":     [".go"],
        }

        return language_extensions[self.lang().lower()]

    def is_file_type(self, file_path: str) -> bool:
        """Check if the file has the specified file extension."""
        for extension in self.get_language_extensions():
            if file_path.endswith(extension):
                return True
        return False

    def is_test_file(self, file_content, lang):
        """Determine if the file content suggests it is a test file."""
        test_indicators = []
        if self.lang() == "python":
            test_indicators = ["import unittest", "import pytest", "from unittest", "from pytest"]
        elif self.lang() == "go":
            test_indicators = ["import testing", "func Test"]
        return any(indicator in file_content for indicator in test_indicators)

    def is_likely_useful_file(self, file_path):
        """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
        excluded_dirs = ["docs", "examples", "tests", "test", "scripts", "utils", "benchmarks"]
        utility_or_config_files = []
        github_workflow_or_docs = [".github", ".gitignore", "LICENSE", "README"]

        if self.lang == "python":
            excluded_dirs.append("__pycache__")
            utility_or_config_files.extend(["hubconf.py", "setup.py"])
            github_workflow_or_docs.extend(["stale.py", "gen-card-", "write_model_card"])
        elif self.lang == "go":
            excluded_dirs.append("vendor")
            utility_or_config_files.extend(["go.mod", "go.sum", "Makefile"])

        if any(part.startswith('.') for part in file_path.split('/')):
            return False
        if 'test' in file_path.lower():
            return False
        for excluded_dir in excluded_dirs:
            if f"/{excluded_dir}/" in file_path or file_path.startswith(excluded_dir + "/"):
                return False
        for file_name in utility_or_config_files:
            if file_name in file_path:
                return False
        for doc_file in github_workflow_or_docs:
            if doc_file in file_path:
                return False
        return True

    def has_sufficient_content(self, file_content, min_line_count=10):
        """Check if the file has a minimum number of substantive lines."""
        lines = [line for line in file_content.split('\n') if line.strip() and not line.strip().startswith(('#', '//'))]
        return len(lines) >= min_line_count

    def remove_comments_and_docstrings(self, source):
        """Remove comments and docstrings from the Python source code."""
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                node.body = node.body[1:]  # Remove docstring
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                node.value.value = ""  # Remove comments
        return ast.unparse(tree)


def main():
    com = Utils(lang="Python")


if __name__ == '__main__':
    main()
