"""Generic Markdown exporter for CodeContext-Bridge."""

from pathlib import Path
from typing import Optional

from .base import BaseExporter


class GenericExporter(BaseExporter):
    """Export project context as generic Markdown."""

    @property
    def name(self) -> str:
        return "generic"

    @property
    def description(self) -> str:
        return "Generic Markdown format"

    def export(self, output_path: Optional[Path] = None, max_tokens: int = 80000) -> str:
        """Export context as generic Markdown."""
        lines = [
            self._generate_header(),
            self._generate_structure(),
            self._generate_dependencies(),
        ]

        # Key files
        if self.context.key_files:
            lines.extend(["## 🔑 Key Files", ""])
            for purpose, filename in self.context.key_files.items():
                lines.append(f"- **{purpose}:** `{filename}`")
            lines.append("")

        # Git info
        if self.context.git_info:
            lines.extend(["## 🔀 Git Information", ""])
            lines.append(f"- **Branch:** {self.context.git_info.get('branch', 'unknown')}")
            lines.append(f"- **Total Commits:** {self.context.git_info.get('commit_count', 0)}")
            if self.context.git_info.get('remote_url'):
                lines.append(f"- **Remote URL:** {self.context.git_info['remote_url']}")
            if self.context.git_info.get('last_commit'):
                last = self.context.git_info['last_commit']
                if last.get('message'):
                    lines.append(f"- **Last Commit:** {last['message'][:80]}")
            lines.append("")

        # Source files
        selected_files = self._select_priority_files(max_tokens)
        if selected_files:
            lines.extend([
                "## 📄 Source Files",
                "",
                f"*Showing {len(selected_files)} of {len(self.context.files)} files*",
                "",
            ])

            for file_info in selected_files:
                lines.extend([
                    f"### `{file_info.relative_path}`",
                    "",
                    f"- **Size:** {file_info.size} bytes",
                    f"- **Tokens:** ~{file_info.token_estimate}",
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
