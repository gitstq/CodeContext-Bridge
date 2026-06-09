"""Tests for exporter modules."""

import pytest
from pathlib import Path

from codecontext_bridge.exporters.claude import ClaudeExporter
from codecontext_bridge.exporters.codex import CodexExporter
from codecontext_bridge.exporters.cursor import CursorExporter
from codecontext_bridge.exporters.generic import GenericExporter
from codecontext_bridge.scanner import ProjectContext, scan_project


class TestClaudeExporter:
    def test_export(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        exporter = ClaudeExporter(context)
        content = exporter.export()

        assert context.project_name in content
        assert "main.py" in content
        assert "```python" in content

    def test_export_with_output(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        exporter = ClaudeExporter(context)
        output_path = tmp_path / "output.md"
        exporter.export(output_path=output_path)

        assert output_path.exists()
        assert context.project_name in output_path.read_text()


class TestCodexExporter:
    def test_export(self, tmp_path):
        (tmp_path / "app.js").write_text("console.log('hello')")
        context = scan_project(tmp_path)

        exporter = CodexExporter(context)
        content = exporter.export()

        assert context.project_name in content
        assert "app.js" in content
        assert "```javascript" in content


class TestCursorExporter:
    def test_export(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        exporter = CursorExporter(context)
        content = exporter.export()

        assert context.project_name in content
        assert "Code Conventions" in content
        assert "Python" in content


class TestGenericExporter:
    def test_export(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        context = scan_project(tmp_path)

        exporter = GenericExporter(context)
        content = exporter.export()

        assert context.project_name in content
        assert "Project Structure" in content
        assert "main.py" in content


class TestExporterTokenLimit:
    def test_respects_max_tokens(self, tmp_path):
        # Create many files to exceed token limit
        for i in range(20):
            (tmp_path / f"file{i}.py").write_text(f"x = {i}\n" * 100)

        context = scan_project(tmp_path)

        exporter = GenericExporter(context)
        content = exporter.export(max_tokens=1000)

        # Should be limited
        assert len(content) // 4 < 2000  # Allow some overhead
