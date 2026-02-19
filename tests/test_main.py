"""Tests for niftyregw.__main__ module."""

from typer.testing import CliRunner

from niftyregw.__main__ import app

runner = CliRunner()


def test_app_exists():
    """Test that app exists and is a Typer instance."""
    import typer

    assert isinstance(app, typer.Typer)


def test_app_no_args_shows_help():
    """Test that running app with no args shows help."""
    result = runner.invoke(app, [])
    assert result.exit_code != 0
    assert "Usage" in result.stdout or "Commands" in result.stdout


def test_app_help_flag():
    """Test that --help flag works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "Commands" in result.stdout


def test_app_has_install_command():
    """Test that install command is registered."""
    result = runner.invoke(app, ["install", "--help"])
    # Should show help for install command, not error
    assert "install" in result.stdout.lower() or "Download" in result.stdout


def test_app_has_aladin_command():
    """Test that aladin command is registered."""
    result = runner.invoke(app, ["aladin", "--help"])
    assert "aladin" in result.stdout.lower() or "affine" in result.stdout.lower()


def test_app_has_f3d_command():
    """Test that f3d command is registered."""
    result = runner.invoke(app, ["f3d", "--help"])
    assert "f3d" in result.stdout.lower() or "deformation" in result.stdout.lower()


def test_app_has_measure_command():
    """Test that measure command is registered."""
    result = runner.invoke(app, ["measure", "--help"])
    assert "measure" in result.stdout.lower() or "similarity" in result.stdout.lower()


def test_app_has_jacobian_command():
    """Test that jacobian command is registered."""
    result = runner.invoke(app, ["jacobian", "--help"])
    assert "jacobian" in result.stdout.lower() or "transformation" in result.stdout.lower()


def test_app_has_resample_command():
    """Test that resample command is registered."""
    result = runner.invoke(app, ["resample", "--help"])
    assert "resample" in result.stdout.lower() or "transformation" in result.stdout.lower()


def test_app_has_tools_command():
    """Test that tools command is registered."""
    result = runner.invoke(app, ["tools", "--help"])
    assert "tools" in result.stdout.lower() or "manipulation" in result.stdout.lower()


def test_app_has_average_command():
    """Test that average command is registered."""
    result = runner.invoke(app, ["average", "--help"])
    assert "average" in result.stdout.lower()


def test_app_has_transform_command():
    """Test that transform command is registered."""
    result = runner.invoke(app, ["transform", "--help"])
    assert "transform" in result.stdout.lower()


def test_app_no_completion():
    """Test that completion is disabled."""
    assert app.add_completion is False


def test_app_no_args_is_help():
    """Test that no_args_is_help is enabled."""
    assert app.no_args_is_help is True
