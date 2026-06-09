"""Tests for utility functions."""

import pytest
from pathlib import Path

from codecontext_bridge.utils import (
    format_file_size,
    get_file_extension,
    is_text_file,
    redact_sensitive_data,
    truncate_text,
)


class TestFormatFileSize:
    def test_bytes(self):
        assert format_file_size(512) == "512.0 B"

    def test_kilobytes(self):
        assert format_file_size(1536) == "1.5 KB"

    def test_megabytes(self):
        assert format_file_size(2 * 1024 * 1024) == "2.0 MB"

    def test_gigabytes(self):
        assert format_file_size(3 * 1024 * 1024 * 1024) == "3.0 GB"


class TestTruncateText:
    def test_short_text(self):
        text = "Hello"
        assert truncate_text(text, 100) == "Hello"

    def test_long_text(self):
        text = "A" * 1000
        result = truncate_text(text, 500)
        assert result.endswith("...")
        assert len(result) == 503


class TestRedactSensitiveData:
    def test_api_key(self):
        text = 'api_key = "sk-abc123def456ghi789"'
        result = redact_sensitive_data(text)
        assert "***REDACTED***" in result
        assert "sk-abc123def456ghi789" not in result

    def test_password(self):
        text = 'password = "mysecret123"'
        result = redact_sensitive_data(text)
        assert "***REDACTED***" in result
        assert "mysecret123" not in result

    def test_no_sensitive_data(self):
        text = "This is a normal text without secrets"
        result = redact_sensitive_data(text)
        assert result == text


class TestGetFileExtension:
    def test_with_extension(self):
        assert get_file_extension(Path("test.py")) == ".py"

    def test_no_extension(self):
        assert get_file_extension(Path("Makefile")) == ""

    def test_uppercase(self):
        assert get_file_extension(Path("test.PY")) == ".py"


class TestIsTextFile:
    def test_text_extension(self):
        assert is_text_file(Path("test.py")) is True

    def test_binary_extension(self):
        assert is_text_file(Path("image.png")) is False

    def test_unknown_extension_text_content(self, tmp_path):
        file_path = tmp_path / "unknown.txt"
        file_path.write_text("Hello world")
        assert is_text_file(file_path) is True

    def test_unknown_extension_binary_content(self, tmp_path):
        file_path = tmp_path / "binary.dat"
        file_path.write_bytes(b"\x00\x01\x02\x03")
        assert is_text_file(file_path) is False
