"""Cursor exporter for CodeContext-Bridge."""

from pathlib import Path
from typing import Optional

from .base import BaseExporter


class CursorExporter(BaseExporter):
    """Export project context for Cursor AI Editor."""

    @property
    def name(self) -> str:
        return "cursor"

    @property
    def description(self) -> str:
        return "Cursor AI Editor format (.cursorrules)"

    def export(self, output_path: Optional[Path] = None, max_tokens: int = 80000) -> str:
        """Export context in Cursor .cursorrules format."""
        lines = [
            f"# {self.context.project_name} - Cursor Context",
            "",
            "## Project Rules",
            "",
            f"- Project name: {self.context.project_name}",
            f"- Total files: {len(self.context.files)}",
            "",
        ]

        # Tech stack detection
        tech_stack = []
        if "python" in self.context.dependencies:
            tech_stack.append("Python")
        if "nodejs" in self.context.dependencies:
            tech_stack.append("Node.js/JavaScript")
        if "rust" in self.context.dependencies:
            tech_stack.append("Rust")
        if "go" in self.context.dependencies:
            tech_stack.append("Go")
        if "java" in self.context.dependencies:
            tech_stack.append("Java")

        if tech_stack:
            lines.extend([
                "## Tech Stack",
                "",
                f"Primary technologies: {', '.join(tech_stack)}",
                "",
            ])

        # File type rules
        if self.context.file_types:
            lines.extend(["## File Types", ""])
            sorted_types = sorted(
                self.context.file_types.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_types[:10]:
                lines.append(f"- {ext}: {count} files")
            lines.append("")

        # Dependencies
        if self.context.dependencies:
            lines.extend(["## Dependencies", ""])
            for lang, files in self.context.dependencies.items():
                lines.append(f"- {lang}: {', '.join(files)}")
            lines.append("")

        # Key files
        if self.context.key_files:
            lines.extend(["## Key Configuration Files", ""])
            for purpose, filename in self.context.key_files.items():
                lines.append(f"- {purpose}: {filename}")
            lines.append("")

        # Code conventions based on detected languages
        lines.extend([
            "## Code Conventions",
            "",
        ])

        if ".py" in self.context.file_types:
            lines.extend([
                "### Python",
                "- Follow PEP 8 style guide",
                "- Use type hints where appropriate",
                "- Keep functions focused and small",
                "- Use docstrings for public APIs",
                "",
            ])

        if ".js" in self.context.file_types or ".ts" in self.context.file_types:
            lines.extend([
                "### JavaScript/TypeScript",
                "- Use modern ES6+ syntax",
                "- Prefer const/let over var",
                "- Use async/await for asynchronous code",
                "- Follow the existing module pattern",
                "",
            ])

        if ".go" in self.context.file_types:
            lines.extend([
                "### Go",
                "- Follow gofmt formatting",
                "- Keep functions concise",
                "- Handle errors explicitly",
                "- Use meaningful variable names",
                "",
            ])

        if ".rs" in self.context.file_types:
            lines.extend([
                "### Rust",
                "- Follow rustfmt formatting",
                "- Use Result/Option for error handling",
                "- Prefer immutable bindings",
                "- Document public APIs",
                "",
            ])

        # Source files
        selected_files = self._select_priority_files(max_tokens)
        if selected_files:
            lines.extend(["## Reference Files", ""])

            for file_info in selected_files:
                lines.extend([
                    f"### {file_info.relative_path}",
                    "",
                    f"```{self._get_language(file_info.extension)}",
                    file_info.content or "",
                    "```",
                    "",
                ])

        content = "\n".join(lines)

        if output_path:
            self._write_file(content, output_path)

        return content

    def _get_language(self, extension: str) -> str:
        """Map file extension to markdown code block language."""
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
            ".sh": "bash",
            ".sql": "sql",
            ".dockerfile": "dockerfile",
            ".vue": "vue",
            ".lua": "lua",
            ".r": "r",
            ".dart": "dart",
            ".tf": "hcl",
            ".proto": "protobuf",
        }
        return mapping.get(extension, "")
