"""Base exporter class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from ..scanner import ProjectContext


class BaseExporter(ABC):
    """Base class for all context exporters."""

    def __init__(self, context: ProjectContext):
        self.context = context

    @property
    @abstractmethod
    def name(self) -> str:
        """Exporter name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Exporter description."""
        pass

    @abstractmethod
    def export(self, output_path: Optional[Path] = None, max_tokens: int = 80000) -> str:
        """Export context to the target format.

        Args:
            output_path: Optional path to write output file
            max_tokens: Maximum tokens to include

        Returns:
            The exported content as string
        """
        pass

    def _select_priority_files(self, max_tokens: int) -> List:
        """Select files to include based on priority and token limit.

        Priority order:
        1. Key config files (README, package.json, etc.)
        2. Main source files (shorter files first)
        3. Other text files
        """
        priority_extensions = {
            ".md", ".txt", ".rst",  # Documentation
            ".json", ".yaml", ".yml", ".toml",  # Config
            ".py", ".js", ".ts", ".go", ".rs",  # Source code
        }

        sorted_files = sorted(
            self.context.files,
            key=lambda f: (
                0 if f.relative_path in ["README.md", "README.rst", "README.txt"] else 1,
                0 if f.extension in priority_extensions else 2,
                f.token_estimate,
            ),
        )

        selected = []
        total_tokens = 0

        for file_info in sorted_files:
            if not file_info.is_text or not file_info.content:
                continue

            if total_tokens + file_info.token_estimate > max_tokens:
                break

            selected.append(file_info)
            total_tokens += file_info.token_estimate

        return selected

    def _generate_header(self) -> str:
        """Generate common header for exports."""
        lines = [
            f"# Project Context: {self.context.project_name}",
            "",
            f"**Project Path:** `{self.context.project_path}`",
            f"**Total Files:** {len(self.context.files)}",
            f"**Total Size:** {self.context.total_size / 1024:.1f} KB",
            "",
        ]
        return "\n".join(lines)

    def _generate_structure(self) -> str:
        """Generate project structure overview."""
        lines = ["## 📁 Project Structure", ""]

        # Show file types summary
        if self.context.file_types:
            lines.append("### File Types")
            sorted_types = sorted(
                self.context.file_types.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_types[:15]:
                lines.append(f"- `{ext}`: {count} files")
            lines.append("")

        # Show key directories
        if self.context.directories:
            lines.append("### Key Directories")
            for directory in self.context.directories[:20]:
                if directory != ".":
                    lines.append(f"- `{directory}/`")
            if len(self.context.directories) > 20:
                lines.append(f"- ... and {len(self.context.directories) - 20} more")
            lines.append("")

        return "\n".join(lines)

    def _generate_dependencies(self) -> str:
        """Generate dependencies section."""
        if not self.context.dependencies:
            return ""

        lines = ["## 📦 Dependencies", ""]
        for lang, files in self.context.dependencies.items():
            lines.append(f"### {lang.title()}")
            for f in files:
                lines.append(f"- `{f}`")
            lines.append("")

        return "\n".join(lines)

    def _write_file(self, content: str, output_path: Path) -> None:
        """Write content to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
