"""Utility functions for CodeContext-Bridge."""

import hashlib
import os
import re
from pathlib import Path
from typing import List, Optional, Set

import pathspec


# Default ignore patterns (similar to .gitignore defaults)
DEFAULT_IGNORE_PATTERNS = """
# Version control
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.tox/
.venv/
venv/
env/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.npm
.yarn

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
.ccb/
*.ccb-snapshot
context-exports/
"""


def load_gitignore_spec(project_path: Path) -> Optional[pathspec.PathSpec]:
    """Load .gitignore patterns from project root."""
    gitignore_path = project_path / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            patterns = f.read()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns.splitlines())
    return None


def get_default_ignore_spec() -> pathspec.PathSpec:
    """Get default ignore spec."""
    return pathspec.PathSpec.from_lines(
        "gitwildmatch", DEFAULT_IGNORE_PATTERNS.strip().splitlines()
    )


def should_ignore_file(
    file_path: Path,
    project_path: Path,
    gitignore_spec: Optional[pathspec.PathSpec] = None,
    default_spec: Optional[pathspec.PathSpec] = None,
) -> bool:
    """Check if a file should be ignored based on ignore specs."""
    rel_path = file_path.relative_to(project_path)
    rel_str = str(rel_path).replace(os.sep, "/")

    if default_spec and default_spec.match_file(rel_str):
        return True
    if gitignore_spec and gitignore_spec.match_file(rel_str):
        return True
    return False


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
    except (OSError, IOError):
        return ""
    return hash_md5.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# Sensitive data patterns for privacy protection
SENSITIVE_PATTERNS = [
    (re.compile(r'(api[_-]?key\s*[=:]\s*)["\']?[a-zA-Z0-9_-]{16,}["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(secret\s*[=:]\s*)["\']?[a-zA-Z0-9_-]{16,}["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(password\s*[=:]\s*)["\']?[^"\'\s]+["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(token\s*[=:]\s*)["\']?[a-zA-Z0-9_-]{16,}["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(bearer\s+)['""']?[a-zA-Z0-9_-]{16,}["\']?', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(aws_access_key_id\s*[=:]\s*)["\']?[A-Z0-9]{20}["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(aws_secret_access_key\s*[=:]\s*)["\']?[a-zA-Z0-9/+=]{40}["\']?', re.IGNORECASE), r'\1"***REDACTED***"'),
    (re.compile(r'(private[_-]?key\s*[=:]\s*)["\']?-----BEGIN[^"\']+', re.IGNORECASE), r'\1"***REDACTED***"'),
]


def redact_sensitive_data(text: str) -> str:
    """Redact sensitive data from text content."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def get_file_extension(file_path: Path) -> str:
    """Get file extension in lowercase."""
    return file_path.suffix.lower()


# File extensions considered as text/code files
TEXT_EXTENSIONS: Set[str] = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".r", ".m", ".mm",
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".xml", ".json", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".conf", ".config", ".md", ".rst", ".txt",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd", ".sql", ".graphql",
    ".dockerfile", ".makefile", ".cmake", ".gradle", ".sbt", ".vue", ".svelte",
    ".lua", ".pl", ".pm", ".t", ".erl", ".ex", ".exs", ".elm", ".clj", ".cljs",
    ".hs", ".lhs", ".fs", ".fsx", ".ml", ".mli", ".nim", ".d", ".v", ".cr",
    ".dart", ".groovy", ".jl", ".pas", ".pp", ".lpr", ".coffee", ".litcoffee",
    ".tf", ".hcl", ".nomad", ".pkr", ".rego", ".proto", ".avsc", ".thrift",
}

# Binary file extensions to skip content reading
BINARY_EXTENSIONS: Set[str] = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".db", ".sqlite", ".sqlite3",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp", ".tiff",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".jar", ".war",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".class", ".o", ".obj", ".a", ".lib", ".pyc", ".pyo",
}


def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file based on extension."""
    ext = get_file_extension(file_path)
    if ext in TEXT_EXTENSIONS:
        return True
    if ext in BINARY_EXTENSIONS:
        return False
    # Try to detect by reading first bytes
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            if b"\0" in chunk:
                return False
        return True
    except (OSError, IOError):
        return False


def estimate_token_count(text: str) -> int:
    """Estimate token count using a simple heuristic (roughly 4 chars per token)."""
    return len(text) // 4
