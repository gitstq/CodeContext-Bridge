"""Tests for scanner module."""

import pytest
from pathlib import Path

from codecontext_bridge.scanner import (
    detect_dependencies,
    identify_key_files,
    scan_project,
)


class TestDetectDependencies:
    def test_python_project(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests\npytest")
        deps = detect_dependencies(tmp_path)
        assert "python" in deps

    def test_node_project(self, tmp_path):
        (tmp_path / "package.json").write_text('{"name": "test"}')
        deps = detect_dependencies(tmp_path)
        assert "nodejs" in deps

    def test_rust_project(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text("[package]")
        deps = detect_dependencies(tmp_path)
        assert "rust" in deps

    def test_empty_project(self, tmp_path):
        deps = detect_dependencies(tmp_path)
        assert deps == {}


class TestIdentifyKeyFiles:
    def test_readme(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        key_files = identify_key_files(tmp_path)
        assert "README" in key_files

    def test_license(self, tmp_path):
        (tmp_path / "LICENSE").write_text("MIT")
        key_files = identify_key_files(tmp_path)
        assert "LICENSE" in key_files

    def test_docker(self, tmp_path):
        (tmp_path / "Dockerfile").write_text("FROM python:3.9")
        key_files = identify_key_files(tmp_path)
        assert "Docker" in key_files


class TestScanProject:
    def test_empty_project(self, tmp_path):
        context = scan_project(tmp_path)
        assert context.project_name == tmp_path.name
        assert len(context.files) == 0

    def test_single_file(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)
        assert len(context.files) == 1
        assert context.files[0].relative_path == "main.py"
        assert context.files[0].content == "print('hello')"

    def test_ignored_files(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]")
        context = scan_project(tmp_path)
        assert len(context.files) == 1
        assert all(".git" not in f.relative_path for f in context.files)

    def test_sensitive_data_redaction(self, tmp_path):
        (tmp_path / "config.py").write_text('API_KEY = "sk-secret123456789"')
        context = scan_project(tmp_path, redact_sensitive=True)
        assert len(context.files) == 1
        assert "***REDACTED***" in context.files[0].content
        assert "sk-secret123456789" not in context.files[0].content

    def test_file_types_count(self, tmp_path):
        (tmp_path / "a.py").write_text("a")
        (tmp_path / "b.py").write_text("b")
        (tmp_path / "c.js").write_text("c")
        context = scan_project(tmp_path)
        assert context.file_types[".py"] == 2
        assert context.file_types[".js"] == 1
