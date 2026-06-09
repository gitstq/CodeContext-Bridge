"""Tests for snapshot module."""

import pytest
from pathlib import Path

from codecontext_bridge.scanner import scan_project
from codecontext_bridge.snapshot import SnapshotManager


class TestSnapshotManager:
    def test_save_and_load(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        manager = SnapshotManager(tmp_path)
        snapshot_path = manager.save(context, name="test")

        assert snapshot_path.exists()

        loaded = manager.load("test")
        assert loaded.project_name == context.project_name
        assert len(loaded.files) == len(context.files)

    def test_list_snapshots(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        manager = SnapshotManager(tmp_path)
        manager.save(context, name="snap1")
        manager.save(context, name="snap2")

        snapshots = manager.list_snapshots()
        assert len(snapshots) == 2
        names = [s["name"] for s in snapshots]
        assert "snap1" in names
        assert "snap2" in names

    def test_delete_snapshot(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        manager = SnapshotManager(tmp_path)
        manager.save(context, name="todelete")

        assert manager.delete("todelete") is True
        assert manager.delete("todelete") is False

    def test_snapshot_not_found(self, tmp_path):
        manager = SnapshotManager(tmp_path)
        with pytest.raises(FileNotFoundError):
            manager.load("nonexistent")

    def test_diff_snapshots(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context1 = scan_project(tmp_path)

        manager = SnapshotManager(tmp_path)
        manager.save(context1, name="old")

        (tmp_path / "new.py").write_text("print('world')")
        context2 = scan_project(tmp_path)
        manager.save(context2, name="new")

        diff = manager.get_diff("old", "new")
        assert "new.py" in diff["added"]
        assert diff["unchanged"] == 1  # main.py
