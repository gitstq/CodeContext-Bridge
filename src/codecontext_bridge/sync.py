"""Sync engine for CodeContext-Bridge."""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .exporters.claude import ClaudeExporter
from .exporters.codex import CodexExporter
from .exporters.cursor import CursorExporter
from .exporters.generic import GenericExporter
from .scanner import ProjectContext

console = Console()

# Registry of available exporters
EXPORTERS = {
    "claude": ClaudeExporter,
    "codex": CodexExporter,
    "cursor": CursorExporter,
    "generic": GenericExporter,
}


def list_exporters() -> Table:
    """Return a table of available exporters."""
    table = Table(title="Available Exporters")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")

    for name, exporter_class in EXPORTERS.items():
        # Create a dummy instance to get description
        dummy_context = ProjectContext(
            project_path=Path("."),
            project_name="dummy",
        )
        exporter = exporter_class(dummy_context)
        table.add_row(name, exporter.description)

    return table


def sync_context(
    context: ProjectContext,
    target: str,
    output_dir: Optional[Path] = None,
    max_tokens: int = 80000,
    copy_to_clipboard: bool = False,
) -> Path:
    """Sync project context to a target AI assistant format.

    Args:
        context: The project context to sync
        target: Target format name (claude, codex, cursor, generic)
        output_dir: Directory to write output file
        max_tokens: Maximum tokens to include
        copy_to_clipboard: Whether to copy output to clipboard

    Returns:
        Path to the generated file
    """
    if target not in EXPORTERS:
        raise ValueError(
            f"Unknown target: {target}. Available: {', '.join(EXPORTERS.keys())}"
        )

    exporter_class = EXPORTERS[target]
    exporter = exporter_class(context)

    # Determine output path
    if output_dir is None:
        output_dir = context.project_path / "context-exports"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    safe_name = context.project_name.replace(" ", "_").replace("/", "_")
    if target == "cursor":
        filename = f"{safe_name}.cursorrules"
    elif target == "claude":
        filename = f"{safe_name}-CLAUDE.md"
    else:
        filename = f"{safe_name}-{target}-context.md"

    output_path = output_dir / filename

    # Export
    console.print(f"🔄 Exporting context for [bold cyan]{target}[/]...")
    content = exporter.export(output_path=output_path, max_tokens=max_tokens)

    # Show summary
    file_size = output_path.stat().st_size
    console.print(Panel(
        f"✅ Context exported successfully!\n"
        f"📄 File: {output_path}\n"
        f"💾 Size: {file_size / 1024:.1f} KB\n"
        f"🔤 Estimated tokens: {len(content) // 4:,}",
        title="Export Complete",
        border_style="green",
    ))

    # Copy to clipboard if requested
    if copy_to_clipboard:
        try:
            import pyperclip
            pyperclip.copy(content)
            console.print("📋 Content copied to clipboard!")
        except ImportError:
            console.print(
                "[yellow]⚠️  pyperclip not installed. Install with: pip install pyperclip[/]"
            )

    return output_path


def sync_all(
    context: ProjectContext,
    output_dir: Optional[Path] = None,
    max_tokens: int = 80000,
) -> Dict[str, Path]:
    """Sync project context to all available formats.

    Args:
        context: The project context to sync
        output_dir: Directory to write output files
        max_tokens: Maximum tokens per export

    Returns:
        Dict mapping target name to output path
    """
    results = {}

    console.print("🚀 Syncing to all available formats...")

    for target in EXPORTERS.keys():
        try:
            path = sync_context(
                context=context,
                target=target,
                output_dir=output_dir,
                max_tokens=max_tokens,
            )
            results[target] = path
        except Exception as e:
            console.print(f"[red]❌ Failed to export for {target}: {e}[/]")

    return results
