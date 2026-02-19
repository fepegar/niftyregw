"""Tests for niftyregw.commands.__init__ module."""

import sys
from unittest.mock import Mock, patch

import pytest
import typer

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel


def test_setup_logger_debug():
    """Test setup_logger with DEBUG level."""
    with patch("loguru.logger.remove") as mock_remove, patch(
        "loguru.logger.add"
    ) as mock_add:
        setup_logger(LogLevel.DEBUG)
        mock_remove.assert_called_once()
        mock_add.assert_called_once()
        call_args = mock_add.call_args
        assert call_args[1]["level"] == "DEBUG"


def test_setup_logger_info():
    """Test setup_logger with INFO level."""
    with patch("loguru.logger.remove") as mock_remove, patch(
        "loguru.logger.add"
    ) as mock_add:
        setup_logger(LogLevel.INFO)
        mock_remove.assert_called_once()
        mock_add.assert_called_once()
        call_args = mock_add.call_args
        assert call_args[1]["level"] == "INFO"


def test_setup_logger_warning():
    """Test setup_logger with WARNING level."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add") as mock_add:
        setup_logger(LogLevel.WARNING)
        call_args = mock_add.call_args
        assert call_args[1]["level"] == "WARNING"


def test_setup_logger_error():
    """Test setup_logger with ERROR level."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add") as mock_add:
        setup_logger(LogLevel.ERROR)
        call_args = mock_add.call_args
        assert call_args[1]["level"] == "ERROR"


def test_setup_logger_format():
    """Test setup_logger uses correct format."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add") as mock_add, patch(
        "loguru.logger.configure"
    ):
        setup_logger(LogLevel.DEBUG)
        call_args = mock_add.call_args
        format_str = call_args[1]["format"]
        # Check key elements are present
        assert "time" in format_str
        assert "executable" in format_str
        assert "level" in format_str
        assert "message" in format_str


def test_setup_logger_configures_default_executable():
    """Test setup_logger sets a default executable in extra to avoid KeyError."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add"), patch(
        "loguru.logger.configure"
    ) as mock_configure:
        setup_logger(LogLevel.DEBUG)
        mock_configure.assert_called_once_with(extra={"executable": "niftyregw"})


def test_setup_logger_colorize():
    """Test setup_logger enables colorize."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add") as mock_add:
        setup_logger(LogLevel.DEBUG)
        call_args = mock_add.call_args
        assert call_args[1]["colorize"] is True


def test_setup_logger_stderr():
    """Test setup_logger outputs to stderr."""
    with patch("loguru.logger.remove"), patch("loguru.logger.add") as mock_add:
        setup_logger(LogLevel.DEBUG)
        call_args = mock_add.call_args
        assert call_args[0][0] == sys.stderr


def test_make_help_callback_creates_callable():
    """Test make_help_callback returns a callable."""
    callback = make_help_callback("reg_aladin")
    assert callable(callback)


def test_make_help_callback_exits_when_true():
    """Test help callback exits when value is True."""
    callback = make_help_callback("reg_aladin")

    with (
        patch("niftyregw.commands.run") as mock_run,
        pytest.raises(typer.Exit),
    ):
        callback(True)
        mock_run.assert_called_once_with("reg_aladin", "-h")


def test_make_help_callback_does_nothing_when_false():
    """Test help callback does nothing when value is False."""
    callback = make_help_callback("reg_aladin")

    with patch("niftyregw.commands.run") as mock_run:
        result = callback(False)
        mock_run.assert_not_called()
        assert result is None


def test_make_version_callback_creates_callable():
    """Test make_version_callback returns a callable."""
    callback = make_version_callback("reg_aladin")
    assert callable(callback)


def test_make_version_callback_exits_when_true():
    """Test version callback exits when value is True."""
    callback = make_version_callback("reg_aladin")

    with (
        patch("niftyregw.commands.run") as mock_run,
        pytest.raises(typer.Exit),
    ):
        callback(True)
        mock_run.assert_called_once_with("reg_aladin", "--version")


def test_make_version_callback_does_nothing_when_false():
    """Test version callback does nothing when value is False."""
    callback = make_version_callback("reg_aladin")

    with patch("niftyregw.commands.run") as mock_run:
        result = callback(False)
        mock_run.assert_not_called()
        assert result is None


def test_make_help_callback_with_different_tools():
    """Test make_help_callback works with different tool names."""
    tools = ["reg_aladin", "reg_f3d", "reg_measure"]
    for tool in tools:
        callback = make_help_callback(tool)
        with (
            patch("niftyregw.commands.run") as mock_run,
            pytest.raises(typer.Exit),
        ):
            callback(True)
            # Check that run was called with the correct tool
            assert mock_run.call_args[0][0] == tool


def test_make_version_callback_with_different_tools():
    """Test make_version_callback works with different tool names."""
    tools = ["reg_aladin", "reg_f3d", "reg_measure"]
    for tool in tools:
        callback = make_version_callback(tool)
        with (
            patch("niftyregw.commands.run") as mock_run,
            pytest.raises(typer.Exit),
        ):
            callback(True)
            # Check that run was called with the correct tool
            assert mock_run.call_args[0][0] == tool
