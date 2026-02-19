"""Tests for niftyregw.enums module."""

from niftyregw.enums import LogLevel


def test_log_level_enum_values():
    """Test that LogLevel enum has expected values."""
    assert LogLevel.DEBUG.value == "DEBUG"
    assert LogLevel.INFO.value == "INFO"
    assert LogLevel.WARNING.value == "WARNING"
    assert LogLevel.ERROR.value == "ERROR"


def test_log_level_enum_members():
    """Test that LogLevel enum has expected members."""
    assert hasattr(LogLevel, "DEBUG")
    assert hasattr(LogLevel, "INFO")
    assert hasattr(LogLevel, "WARNING")
    assert hasattr(LogLevel, "ERROR")


def test_log_level_enum_count():
    """Test that LogLevel enum has exactly 4 members."""
    assert len(list(LogLevel)) == 4
