"""Claude Code exporter for CodeContext-Bridge."""

from pathlib import Path
from typing import Optional

from .base import BaseExporter


class ClaudeExporter(BaseExporter):
    """Export project context for Claude Code (CLAUDE.md format)."""

    @property
    def name(self) -> str:
        return "claude"

    @property
    def description(self) -> str:
        return "Claude Code format (CLAUDE.md)"

    def export(self, output_path: Optional[Path] = None, max_tokens: int = 80000) -> str:
        """Export context in Claude Code CLAUDE.md format."""
        lines = [
            f"# {self.context.project_name}",
            "",
            f"This is the project context for `{self.context.project_name}`. Use this information to understand the codebase structure, dependencies, and key files.",
            "",
            "## Project Overview",
            "",
            f"- **Name:** {self.context.project_name}",
            f"- **Path:** `{self.context.project_path}`",
            f"- **Total Files:** {len(self.context.files)}",
            "",
        ]

        # Git info
        if self.context.git_info:
            lines.extend([
                "## Git Repository",
                "",
                f"- **Branch:** {self.context.git_info.get('branch', 'unknown')}",
                f"- **Commits:** {self.context.git_info.get('commit_count', 0)}",
            ])
            if self.context.git_info.get('remote_url'):
                lines.append(f"- **Remote:** {self.context.git_info['remote_url']}")
            lines.append("")

        # Dependencies
        if self.context.dependencies:
            lines.extend(["## Dependencies", ""])
            for lang, files in self.context.dependencies.items():
                lines.append(f"### {lang.title()}")
                for f in files:
                    lines.append(f"- `{f}`")
                lines.append("")

        # File types
        if self.context.file_types:
            lines.extend(["## File Types", ""])
            sorted_types = sorted(
                self.context.file_types.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_types[:15]:
                lines.append(f"- `{ext}`: {count} files")
            lines.append("")

        # Key files
        if self.context.key_files:
            lines.extend(["## Key Files", ""])
            for purpose, filename in self.context.key_files.items():
                lines.append(f"- **{purpose}:** `{filename}`")
            lines.append("")

        # File contents
        selected_files = self._select_priority_files(max_tokens)
        if selected_files:
            lines.extend(["## Source Files", ""])
            lines.append(f"*Showing {len(selected_files)} of {len(self.context.files)} files*")
            lines.append("")

            for file_info in selected_files:
                lines.extend([
                    f"### `{file_info.relative_path}`",
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
            ".htm": "html",
            ".css": "css",
            ".scss": "scss",
            ".sass": "sass",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".sql": "sql",
            ".dockerfile": "dockerfile",
            ".vue": "vue",
            ".lua": "lua",
            ".r": "r",
            ".dart": "dart",
            ".groovy": "groovy",
            ".gradle": "groovy",
            ".tf": "hcl",
            ".proto": "protobuf",
        }
        return mapping.get(extension, "")
