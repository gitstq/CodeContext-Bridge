"""CLI entry point for CodeContext-Bridge."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from . import __version__
from .scanner import ProjectContext, get_project_summary, scan_project
from .snapshot import SnapshotManager
from .sync import list_exporters, sync_all, sync_context

app = typer.Typer(
    name="codecontext-bridge",
    help="🔄 Seamlessly migrate and sync project context across AI coding assistants",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"CodeContext-Bridge [bold cyan]v{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """CodeContext-Bridge - AI Coding Assistant Context Manager."""
    pass


@app.command("scan")
def cmd_scan(
    path: Path = typer.Argument(
        ".",
        help="Path to the project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    max_size: int = typer.Option(
        1024 * 1024,
        "--max-size",
        "-s",
        help="Maximum file size to read (bytes)",
    ),
    no_redact: bool = typer.Option(
        False,
        "--no-redact",
        help="Disable sensitive data redaction",
    ),
) -> None:
    """🔍 Scan a project and display its structure."""
    console.print(Panel(
        f"Scanning project at: [bold]{path}[/]",
        title="CodeContext-Bridge",
        border_style="blue",
    ))

    try:
        context = scan_project(
            project_path=path,
            max_file_size=max_size,
            redact_sensitive=not no_redact,
        )

        console.print(get_project_summary(context))

        # Show file tree
        tree = Tree(f"📁 {context.project_name}")
        for directory in context.directories[:20]:
            if directory != ".":
                tree.add(f"📂 {directory}/")
        if len(context.directories) > 20:
            tree.add(f"... and {len(context.directories) - 20} more directories")

        console.print("\n")
        console.print(tree)

    except Exception as e:
        console.print(f"[red]❌ Error scanning project: {e}[/]")
        raise typer.Exit(1)


@app.command("snapshot")
def cmd_snapshot(
    action: str = typer.Argument(
        ...,
        help="Action: create, list, load, delete, diff",
    ),
    path: Path = typer.Argument(
        ".",
        help="Path to the project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Snapshot name",
    ),
    compare: Optional[str] = typer.Option(
        None,
        "--compare",
        "-c",
        help="Compare with another snapshot (for diff action)",
    ),
    max_size: int = typer.Option(
        1024 * 1024,
        "--max-size",
        "-s",
        help="Maximum file size to read (bytes)",
    ),
) -> None:
    """💾 Manage project context snapshots."""
    manager = SnapshotManager(path)

    if action == "create":
        console.print(f"📸 Creating snapshot of [bold]{path.name}[/]...")
        try:
            context = scan_project(project_path=path, max_file_size=max_size)
            snapshot_path = manager.save(context, name=name)
            console.print(f"[green]✅ Snapshot saved: {snapshot_path.name}[/]")
        except Exception as e:
            console.print(f"[red]❌ Error creating snapshot: {e}[/]")
            raise typer.Exit(1)

    elif action == "list":
        snapshots = manager.list_snapshots()
        if not snapshots:
            console.print("[yellow]📭 No snapshots found.[/]")
            return

        table = Table(title=f"Snapshots for {path.name}")
        table.add_column("Name", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Files", style="yellow")
        table.add_column("Tokens", style="magenta")
        table.add_column("Size", style="blue")

        for snap in snapshots:
            size_kb = snap["size_bytes"] / 1024
            table.add_row(
                snap["name"],
                snap["created_at"],
                str(snap["total_files"]),
                f"{snap['total_tokens']:,}",
                f"{size_kb:.1f} KB",
            )

        console.print(table)

    elif action == "load":
        if not name:
            console.print("[red]❌ Snapshot name required (--name)[/]")
            raise typer.Exit(1)

        try:
            context = manager.load(name)
            console.print(get_project_summary(context))
        except FileNotFoundError:
            console.print(f"[red]❌ Snapshot not found: {name}[/]")
            raise typer.Exit(1)

    elif action == "delete":
        if not name:
            console.print("[red]❌ Snapshot name required (--name)[/]")
            raise typer.Exit(1)

        if manager.delete(name):
            console.print(f"[green]✅ Deleted snapshot: {name}[/]")
        else:
            console.print(f"[red]❌ Snapshot not found: {name}[/]")
            raise typer.Exit(1)

    elif action == "diff":
        if not name or not compare:
            console.print("[red]❌ Both --name and --compare required for diff[/]")
            raise typer.Exit(1)

        try:
            diff = manager.get_diff(name, compare)
            console.print(Panel(
                f"Comparing [cyan]{name}[/] → [green]{compare}[/]\n\n"
                f"➕ Added: {len(diff['added'])}\n"
                f"➖ Removed: {len(diff['removed'])}\n"
                f"📝 Modified: {len(diff['modified'])}\n"
                f"✓ Unchanged: {diff['unchanged']}",
                title="Snapshot Diff",
                border_style="blue",
            ))

            if diff["added"]:
                console.print("\n[green]Added files:[/]")
                for f in diff["added"]:
                    console.print(f"  + {f}")

            if diff["removed"]:
                console.print("\n[red]Removed files:[/]")
                for f in diff["removed"]:
                    console.print(f"  - {f}")

            if diff["modified"]:
                console.print("\n[yellow]Modified files:[/]")
                for f in diff["modified"]:
                    console.print(f"  ~ {f}")

        except FileNotFoundError as e:
            console.print(f"[red]❌ {e}[/]")
            raise typer.Exit(1)

    else:
        console.print(f"[red]❌ Unknown action: {action}[/]")
        console.print("Available actions: create, list, load, delete, diff")
        raise typer.Exit(1)


@app.command("export")
def cmd_export(
    target: str = typer.Argument(
        ...,
        help="Target format (claude, codex, cursor, generic)",
    ),
    path: Path = typer.Argument(
        ".",
        help="Path to the project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory",
    ),
    max_tokens: int = typer.Option(
        80000,
        "--max-tokens",
        "-t",
        help="Maximum tokens to include",
    ),
    max_size: int = typer.Option(
        1024 * 1024,
        "--max-size",
        "-s",
        help="Maximum file size to read (bytes)",
    ),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy output to clipboard",
    ),
) -> None:
    """📤 Export project context to an AI assistant format."""
    console.print(f"🔄 Exporting [bold]{path.name}[/] for [cyan]{target}[/]...")

    try:
        context = scan_project(project_path=path, max_file_size=max_size)
        sync_context(
            context=context,
            target=target,
            output_dir=output,
            max_tokens=max_tokens,
            copy_to_clipboard=clipboard,
        )
    except Exception as e:
        console.print(f"[red]❌ Error exporting: {e}[/]")
        raise typer.Exit(1)


@app.command("export-all")
def cmd_export_all(
    path: Path = typer.Argument(
        ".",
        help="Path to the project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory",
    ),
    max_tokens: int = typer.Option(
        80000,
        "--max-tokens",
        "-t",
        help="Maximum tokens per export",
    ),
    max_size: int = typer.Option(
        1024 * 1024,
        "--max-size",
        "-s",
        help="Maximum file size to read (bytes)",
    ),
) -> None:
    """🚀 Export project context to all AI assistant formats."""
    console.print(Panel(
        f"Exporting [bold]{path.name}[/] to all formats...",
        title="Export All",
        border_style="blue",
    ))

    try:
        context = scan_project(project_path=path, max_file_size=max_size)
        results = sync_all(
            context=context,
            output_dir=output,
            max_tokens=max_tokens,
        )

        table = Table(title="Export Results")
        table.add_column("Format", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Status", style="yellow")

        for target, file_path in results.items():
            size_kb = file_path.stat().st_size / 1024
            table.add_row(target, str(file_path.name), f"✅ {size_kb:.1f} KB")

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error exporting: {e}[/]")
        raise typer.Exit(1)


@app.command("list-formats")
def cmd_list_formats() -> None:
    """📋 List all available export formats."""
    console.print(list_exporters())


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
