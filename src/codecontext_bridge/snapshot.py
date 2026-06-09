"""Snapshot management module for CodeContext-Bridge."""

import json
import zlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .scanner import FileInfo, ProjectContext


class SnapshotManager:
    """Manages project context snapshots."""

    SNAPSHOT_DIR = ".ccb"
    SNAPSHOT_EXT = ".ccb-snapshot"

    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.snapshot_dir = self.project_path / self.SNAPSHOT_DIR

    def _ensure_snapshot_dir(self) -> None:
        """Ensure snapshot directory exists."""
        self.snapshot_dir.mkdir(exist_ok=True)

    def _get_snapshot_path(self, name: str) -> Path:
        """Get the file path for a snapshot."""
        safe_name = name.replace("/", "_").replace("\\", "_")
        return self.snapshot_dir / f"{safe_name}{self.SNAPSHOT_EXT}"

    def save(self, context: ProjectContext, name: Optional[str] = None) -> Path:
        """Save a project context snapshot.

        Args:
            context: The project context to save
            name: Optional snapshot name (defaults to timestamp)

        Returns:
            Path to the saved snapshot file
        """
        self._ensure_snapshot_dir()

        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        snapshot_path = self._get_snapshot_path(name)

        # Convert context to serializable dict
        data = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "project_name": context.project_name,
            "project_path": str(context.project_path),
            "summary": {
                "total_files": len(context.files),
                "total_size": context.total_size,
                "total_tokens": context.total_tokens,
                "file_types": context.file_types,
            },
            "git_info": context.git_info,
            "dependencies": context.dependencies,
            "key_files": context.key_files,
            "files": [
                {
                    "relative_path": f.relative_path,
                    "size": f.size,
                    "extension": f.extension,
                    "is_text": f.is_text,
                    "hash": f.hash,
                    "token_estimate": f.token_estimate,
                    "content": f.content,
                }
                for f in context.files
            ],
            "directories": context.directories,
        }

        # Compress and save
        json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        compressed = zlib.compress(json_bytes)

        with open(snapshot_path, "wb") as f:
            f.write(compressed)

        return snapshot_path

    def load(self, name: str) -> ProjectContext:
        """Load a project context snapshot.

        Args:
            name: Snapshot name

        Returns:
            Reconstructed ProjectContext
        """
        snapshot_path = self._get_snapshot_path(name)

        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

        with open(snapshot_path, "rb") as f:
            compressed = f.read()

        json_bytes = zlib.decompress(compressed)
        data = json.loads(json_bytes.decode("utf-8"))

        context = ProjectContext(
            project_path=Path(data["project_path"]),
            project_name=data["project_name"],
            git_info=data.get("git_info"),
            dependencies=data.get("dependencies", {}),
            key_files=data.get("key_files", {}),
            directories=data.get("directories", []),
        )

        for f_data in data.get("files", []):
            file_info = FileInfo(
                path=context.project_path / f_data["relative_path"],
                relative_path=f_data["relative_path"],
                size=f_data["size"],
                extension=f_data["extension"],
                is_text=f_data["is_text"],
                hash=f_data["hash"],
                content=f_data.get("content"),
                token_estimate=f_data.get("token_estimate", 0),
            )
            context.files.append(file_info)
            context.total_size += file_info.size
            context.total_tokens += file_info.token_estimate

        context.file_types = data.get("summary", {}).get("file_types", {})

        return context

    def list_snapshots(self) -> List[Dict]:
        """List all available snapshots.

        Returns:
            List of snapshot metadata dicts
        """
        if not self.snapshot_dir.exists():
            return []

        snapshots = []
        for snapshot_file in self.snapshot_dir.glob(f"*{self.SNAPSHOT_EXT}"):
            try:
                with open(snapshot_file, "rb") as f:
                    compressed = f.read()
                json_bytes = zlib.decompress(compressed)
                data = json.loads(json_bytes.decode("utf-8"))

                snapshots.append({
                    "name": snapshot_file.stem,
                    "created_at": data.get("created_at", "unknown"),
                    "project_name": data.get("project_name", "unknown"),
                    "total_files": data.get("summary", {}).get("total_files", 0),
                    "total_tokens": data.get("summary", {}).get("total_tokens", 0),
                    "size_bytes": len(compressed),
                })
            except (OSError, zlib.error, json.JSONDecodeError):
                continue

        return sorted(snapshots, key=lambda x: x["created_at"], reverse=True)

    def delete(self, name: str) -> bool:
        """Delete a snapshot.

        Args:
            name: Snapshot name

        Returns:
            True if deleted, False if not found
        """
        snapshot_path = self._get_snapshot_path(name)
        if snapshot_path.exists():
            snapshot_path.unlink()
            return True
        return False

    def get_diff(self, old_name: str, new_name: str) -> Dict:
        """Get the difference between two snapshots.

        Args:
            old_name: Name of the older snapshot
            new_name: Name of the newer snapshot

        Returns:
            Dict with added, removed, and modified files
        """
        old_context = self.load(old_name)
        new_context = self.load(new_name)

        old_files = {f.relative_path: f for f in old_context.files}
        new_files = {f.relative_path: f for f in new_context.files}

        added = []
        removed = []
        modified = []

        for rel_path, file_info in new_files.items():
            if rel_path not in old_files:
                added.append(rel_path)
            elif old_files[rel_path].hash != file_info.hash:
                modified.append(rel_path)

        for rel_path in old_files:
            if rel_path not in new_files:
                removed.append(rel_path)

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": len(new_files) - len(added) - len(modified),
        }
