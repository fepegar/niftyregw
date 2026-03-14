"""Tests for niftyregw.commands.install module."""

from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from niftyregw.commands.install import install

runner = CliRunner()


def test_install_default_output_dir(temp_dir):
    """Test install with default output directory."""
    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger") as mock_setup_logger,
    ):
        mock_download.return_value = [Path("/usr/local/bin/reg_aladin")]

        # Create a Typer app and add the command
        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert mock_download.called
        assert mock_setup_logger.called


def test_install_custom_output_dir(temp_dir):
    """Test install with custom output directory."""
    custom_dir = temp_dir / "custom"

    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger"),
    ):
        mock_download.return_value = [custom_dir / "reg_aladin"]

        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["--output-dir", str(custom_dir)])

        assert result.exit_code == 0
        mock_download.assert_called_once_with(custom_dir, device="auto")


def test_install_short_option(temp_dir):
    """Test install with -o short option."""
    custom_dir = temp_dir / "custom"

    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger"),
    ):
        mock_download.return_value = [custom_dir / "reg_aladin"]

        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["-o", str(custom_dir)])

        assert result.exit_code == 0
        mock_download.assert_called_once_with(custom_dir, device="auto")


def test_install_displays_installed_binaries(temp_dir):
    """Test install logs installed binaries."""
    custom_dir = temp_dir / "custom"
    installed_files = [
        custom_dir / "reg_aladin",
        custom_dir / "reg_f3d",
    ]

    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger"),
        patch("niftyregw.commands.install.logger") as mock_logger,
    ):
        mock_download.return_value = installed_files
        mock_bound_logger = mock_logger.bind.return_value

        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["-o", str(custom_dir)])

        assert result.exit_code == 0
        logged_messages = [
            call.args[0] for call in mock_bound_logger.info.call_args_list
        ]
        assert any("reg_aladin" in msg for msg in logged_messages)
        assert any("reg_f3d" in msg for msg in logged_messages)
        assert any("2 binaries installed" in msg for msg in logged_messages)


def test_install_help():
    """Test install --help."""
    app = typer.Typer()
    app.command()(install)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "install" in result.stdout.lower() or "download" in result.stdout.lower()


def test_install_with_device_gpu(temp_dir):
    """Test install with --device gpu."""
    custom_dir = temp_dir / "custom"

    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger"),
    ):
        mock_download.return_value = [custom_dir / "reg_aladin"]

        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["-o", str(custom_dir), "--device", "gpu"])

        assert result.exit_code == 0
        mock_download.assert_called_once_with(custom_dir, device="gpu")


def test_install_with_device_cpu(temp_dir):
    """Test install with --device cpu."""
    custom_dir = temp_dir / "custom"

    with (
        patch("niftyregw.commands.install.download_niftyreg") as mock_download,
        patch("niftyregw.commands.install.setup_logger"),
    ):
        mock_download.return_value = [custom_dir / "reg_aladin"]

        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["-o", str(custom_dir), "--device", "cpu"])

        assert result.exit_code == 0
        mock_download.assert_called_once_with(custom_dir, device="cpu")


def test_install_platform_with_device(temp_dir):
    """Test install --platform respects --device."""
    with (
        patch("niftyregw.commands.install.setup_logger"),
        patch(
            "niftyregw.commands.install.get_platform", return_value="Ubuntu-CUDA"
        ) as mock_gp,
    ):
        app = typer.Typer()
        app.command()(install)
        result = runner.invoke(app, ["--platform", "--device", "gpu"])

        assert result.exit_code == 0
        mock_gp.assert_called_once_with("gpu")
