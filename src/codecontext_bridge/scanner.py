"""Project scanner module for CodeContext-Bridge."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import (
    format_file_size,
    get_default_ignore_spec,
    get_file_extension,
    get_file_hash,
    is_text_file,
    load_gitignore_spec,
    redact_sensitive_data,
    should_ignore_file,
)

console = Console()


@dataclass
class FileInfo:
    """Information about a scanned file."""
    path: Path
    relative_path: str
    size: int
    extension: str
    is_text: bool
    hash: str
    content: Optional[str] = None
    token_estimate: int = 0


@dataclass
class ProjectContext:
    """Complete project context snapshot."""
    project_path: Path
    project_name: str
    files: List[FileInfo] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    file_types: Dict[str, int] = field(default_factory=dict)
    total_size: int = 0
    total_tokens: int = 0
    git_info: Optional[Dict] = None
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    key_files: Dict[str, str] = field(default_factory=dict)


def detect_dependencies(project_path: Path) -> Dict[str, List[str]]:
    """Detect project dependencies from common config files."""
    deps: Dict[str, List[str]] = {}

    # Python
    req_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "Pipfile",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
    ]
    python_deps = []
    for req_file in req_files:
        req_path = project_path / req_file
        if req_path.exists():
            try:
                with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    python_deps.append(f"{req_file}: {len(content.splitlines())} lines")
            except (OSError, IOError):
                pass
    if python_deps:
        deps["python"] = python_deps

    # Node.js
    node_files = ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
    node_deps = []
    for node_file in node_files:
        node_path = project_path / node_file
        if node_path.exists():
            node_deps.append(node_file)
    if node_deps:
        deps["nodejs"] = node_deps

    # Rust
    if (project_path / "Cargo.toml").exists():
        deps["rust"] = ["Cargo.toml"]
    if (project_path / "Cargo.lock").exists():
        deps["rust"] = deps.get("rust", []) + ["Cargo.lock"]

    # Go
    if (project_path / "go.mod").exists():
        deps["go"] = ["go.mod"]
    if (project_path / "go.sum").exists():
        deps["go"] = deps.get("go", []) + ["go.sum"]

    # Java
    java_files = ["pom.xml", "build.gradle", "build.gradle.kts"]
    java_deps = [f for f in java_files if (project_path / f).exists()]
    if java_deps:
        deps["java"] = java_deps

    return deps


def get_git_info(project_path: Path) -> Optional[Dict]:
    """Get git repository information."""
    git_dir = project_path / ".git"
    if not git_dir.exists():
        return None

    try:
        import git
        repo = git.Repo(project_path)
        return {
            "is_git_repo": True,
            "branch": repo.active_branch.name if repo.head.is_valid() else "unknown",
            "commit_count": len(list(repo.iter_commits())),
            "remote_url": next((r.url for r in repo.remotes), None),
            "last_commit": {
                "message": repo.head.commit.message.strip() if repo.head.is_valid() else None,
                "author": str(repo.head.commit.author) if repo.head.is_valid() else None,
                "date": str(repo.head.commit.committed_datetime) if repo.head.is_valid() else None,
            },
        }
    except (ImportError, git.InvalidGitRepositoryError, Exception):
        return {"is_git_repo": True, "details": "Git repo detected but could not read details"}


def identify_key_files(project_path: Path) -> Dict[str, str]:
    """Identify key project files and their purposes."""
    key_files = {}

    key_file_map = {
        "README": ["README.md", "README.rst", "README.txt", "README"],
        "LICENSE": ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"],
        "CHANGELOG": ["CHANGELOG.md", "CHANGELOG.txt", "HISTORY.md", "NEWS.md"],
        "CONTRIBUTING": ["CONTRIBUTING.md", "CONTRIBUTING.txt"],
        "Makefile": ["Makefile", "makefile", "GNUmakefile"],
        "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        "CI/CD": [".github/workflows", ".gitlab-ci.yml", ".travis.yml", "azure-pipelines.yml"],
        "Config": ["pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod"],
    }

    for purpose, filenames in key_file_map.items():
        for filename in filenames:
            file_path = project_path / filename
            if file_path.exists():
                if purpose not in key_files:
                    key_files[purpose] = filename
                break

    return key_files


def scan_project(
    project_path: Path,
    max_file_size: int = 1024 * 1024,  # 1MB
    max_total_tokens: int = 100000,
    include_binary_info: bool = True,
    redact_sensitive: bool = True,
) -> ProjectContext:
    """Scan a project directory and build a context snapshot.

    Args:
        project_path: Path to the project directory
        max_file_size: Maximum file size to read content from (bytes)
        max_total_tokens: Maximum estimated tokens to include
        include_binary_info: Whether to include binary file info (without content)
        redact_sensitive: Whether to redact sensitive data from file contents

    Returns:
        ProjectContext with complete project information
    """
    project_path = project_path.resolve()
    project_name = project_path.name

    context = ProjectContext(
        project_path=project_path,
        project_name=project_name,
    )

    gitignore_spec = load_gitignore_spec(project_path)
    default_spec = get_default_ignore_spec()

    # Collect directories
    directories = set()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"🔍 Scanning project: {project_name}", total=None)

        for root, dirs, files in os.walk(project_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(project_path)

            # Filter out ignored directories
            dirs[:] = [
                d for d in dirs
                if not should_ignore_file(
                    root_path / d, project_path, gitignore_spec, default_spec
                )
            ]

            directories.add(str(rel_root))

            for filename in files:
                file_path = root_path / filename

                if should_ignore_file(file_path, project_path, gitignore_spec, default_spec):
                    continue

                try:
                    stat = file_path.stat()
                    size = stat.st_size
                except (OSError, IOError):
                    continue

                rel_path = str(file_path.relative_to(project_path)).replace(os.sep, "/")
                ext = get_file_extension(file_path)
                is_text = is_text_file(file_path)
                file_hash = get_file_hash(file_path)

                content = None
                token_estimate = 0

                if is_text and size <= max_file_size:
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            raw_content = f.read()
                            if redact_sensitive:
                                content = redact_sensitive_data(raw_content)
                            else:
                                content = raw_content
                            token_estimate = len(content) // 4
                    except (OSError, IOError, UnicodeDecodeError):
                        content = None

                file_info = FileInfo(
                    path=file_path,
                    relative_path=rel_path,
                    size=size,
                    extension=ext,
                    is_text=is_text,
                    hash=file_hash,
                    content=content,
                    token_estimate=token_estimate,
                )

                context.files.append(file_info)
                context.total_size += size
                context.total_tokens += token_estimate

                # Track file types
                if ext:
                    context.file_types[ext] = context.file_types.get(ext, 0) + 1
                else:
                    context.file_types["(no extension)"] = context.file_types.get("(no extension)", 0) + 1

    context.directories = sorted(list(directories))
    context.git_info = get_git_info(project_path)
    context.dependencies = detect_dependencies(project_path)
    context.key_files = identify_key_files(project_path)

    return context


def get_project_summary(context: ProjectContext) -> str:
    """Generate a human-readable project summary."""
    lines = [
        f"📁 Project: {context.project_name}",
        f"📂 Path: {context.project_path}",
        f"📊 Files: {len(context.files)}",
        f"📁 Directories: {len(context.directories)}",
        f"💾 Total Size: {format_file_size(context.total_size)}",
        f"🔤 Estimated Tokens: {context.total_tokens:,}",
        "",
        "📋 File Types:",
    ]

    sorted_types = sorted(context.file_types.items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_types[:10]:
        lines.append(f"  {ext}: {count}")

    if context.git_info:
        lines.extend([
            "",
            "🔀 Git Info:",
            f"  Branch: {context.git_info.get('branch', 'unknown')}",
            f"  Commits: {context.git_info.get('commit_count', 0)}",
        ])

    if context.dependencies:
        lines.extend(["", "📦 Dependencies:"])
        for lang, files in context.dependencies.items():
            lines.append(f"  {lang}: {', '.join(files)}")

    if context.key_files:
        lines.extend(["", "🔑 Key Files:"])
        for purpose, filename in context.key_files.items():
            lines.append(f"  {purpose}: {filename}")

    return "\n".join(lines)
