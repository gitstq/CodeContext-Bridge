"""Codex exporter for CodeContext-Bridge."""

from pathlib import Path
from typing import Optional

from .base import BaseExporter


class CodexExporter(BaseExporter):
    """Export project context for OpenAI Codex CLI."""

    @property
    def name(self) -> str:
        return "codex"

    @property
    def description(self) -> str:
        return "OpenAI Codex CLI format"

    def export(self, output_path: Optional[Path] = None, max_tokens: int = 80000) -> str:
        """Export context in Codex-friendly format."""
        lines = [
            f"# Project: {self.context.project_name}",
            "",
            "## Context for AI Assistant",
            "",
            f"You are working on the project `{self.context.project_name}`. Here is the complete context you need to understand the codebase.",
            "",
            "## Project Structure",
            "",
        ]

        # Directory tree
        if self.context.directories:
            lines.append("```")
            for directory in sorted(self.context.directories)[:30]:
                depth = directory.count("/")
                indent = "  " * depth
                name = directory.split("/")[-1] if "/" in directory else directory
                if name == ".":
                    name = self.context.project_name
                lines.append(f"{indent}{name}/")
            if len(self.context.directories) > 30:
                lines.append(f"  ... and {len(self.context.directories) - 30} more directories")
            lines.append("```")
            lines.append("")

        # File summary
        if self.context.file_types:
            lines.extend(["## File Summary", ""])
            sorted_types = sorted(
                self.context.file_types.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_types[:15]:
                lines.append(f"- `{ext}`: {count} files")
            lines.append("")

        # Dependencies
        if self.context.dependencies:
            lines.extend(["## Dependencies & Configuration", ""])
            for lang, files in self.context.dependencies.items():
                lines.append(f"**{lang.title()}:** {', '.join(files)}")
            lines.append("")

        # Key files content
        selected_files = self._select_priority_files(max_tokens)
        if selected_files:
            lines.extend(["## Important Files", ""])

            for file_info in selected_files:
                lines.extend([
                    f"### File: `{file_info.relative_path}`",
                    "",
                    f"```{self._get_language(file_info.extension)}",
                    file_info.content or "",
                    "```",
                    "",
                ])

        # Instructions for Codex
        lines.extend([
            "## Instructions",
            "",
            "When making changes:",
            "1. Follow the existing code style and patterns",
            "2. Update relevant tests if they exist",
            "3. Keep changes minimal and focused",
            "4. Respect the project structure shown above",
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
