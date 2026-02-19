"""Tests for niftyregw.commands.aladin module."""

from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from niftyregw.commands.aladin import aladin

runner = CliRunner()


def test_aladin_minimal_required_args(mock_nifti_image, temp_dir):
    """Test aladin with minimal required arguments."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(app, ["-r", str(ref_img), "-f", str(flo_img)])

        assert result.exit_code == 0
        mock_reg_aladin.assert_called_once()


def test_aladin_with_output_affine(mock_nifti_image, temp_dir):
    """Test aladin with output affine."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    aff_out = temp_dir / "output.txt"
    flo_img.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "-a", str(aff_out)]
        )

        assert result.exit_code == 0
        call_kwargs = mock_reg_aladin.call_args[1]
        assert call_kwargs["output_affine"] == aff_out


def test_aladin_with_rigid_only(mock_nifti_image, temp_dir):
    """Test aladin with rigid_only flag."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "--rigid-only"]
        )

        assert result.exit_code == 0
        call_kwargs = mock_reg_aladin.call_args[1]
        assert call_kwargs["rigid_only"] is True


def test_aladin_with_numeric_params(mock_nifti_image, temp_dir):
    """Test aladin with numeric parameters."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--max-iterations",
                "10",
                "--num-levels",
                "4",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_reg_aladin.call_args[1]
        assert call_kwargs["max_iterations"] == 10
        assert call_kwargs["num_levels"] == 4


def test_aladin_missing_required_args():
    """Test aladin with missing required arguments."""
    app = typer.Typer()
    app.command()(aladin)
    result = runner.invoke(app, [])

    # Should fail due to missing required arguments
    assert result.exit_code != 0


def test_aladin_help():
    """Test aladin --help."""
    app = typer.Typer()
    app.command()(aladin)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "reference" in result.stdout.lower()
    assert "floating" in result.stdout.lower()


def test_aladin_version_callback():
    """Test aladin version callback exists and is configured."""
    import inspect

    sig = inspect.signature(aladin)
    version_param = sig.parameters["version"]
    # Check it has a callback configured
    assert version_param.annotation is not inspect.Parameter.empty


def test_aladin_help_callback():
    """Test aladin help callback exists and is configured."""
    import inspect

    sig = inspect.signature(aladin)
    help_param = sig.parameters["_"]
    # Check it has a callback configured
    assert help_param.annotation is not inspect.Parameter.empty


def test_aladin_with_all_boolean_flags(mock_nifti_image, temp_dir):
    """Test aladin with all boolean flags."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--no-symmetric",
                "--rigid-only",
                "--affine-direct",
                "--use-nifti-origin",
                "--isotropic",
                "--verbose-off",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_reg_aladin.call_args[1]
        assert call_kwargs["no_symmetric"] is True
        assert call_kwargs["rigid_only"] is True
        assert call_kwargs["affine_direct"] is True
        assert call_kwargs["use_nifti_origin"] is True
        assert call_kwargs["isotropic"] is True
        assert call_kwargs["verbose_off"] is True


def test_aladin_with_masks(mock_nifti_image, temp_dir):
    """Test aladin with mask images."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    ref_mask = temp_dir / "ref_mask.nii.gz"
    flo_mask = temp_dir / "flo_mask.nii.gz"
    flo_img.touch()
    ref_mask.touch()
    flo_mask.touch()

    with (
        patch("niftyregw.commands.aladin.setup_logger"),
        patch("niftyregw.commands.aladin._reg_aladin") as mock_reg_aladin,
    ):
        app = typer.Typer()
        app.command()(aladin)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--reference-mask",
                str(ref_mask),
                "--floating-mask",
                str(flo_mask),
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_reg_aladin.call_args[1]
        assert call_kwargs["reference_mask"] == ref_mask
        assert call_kwargs["floating_mask"] == flo_mask


def test_aladin_log_level_default():
    """Test aladin uses DEBUG log level by default."""
    from niftyregw.enums import LogLevel

    app = typer.Typer()
    app.command()(aladin)

    # Check the default value in the function signature
    import inspect

    sig = inspect.signature(aladin)
    log_level_param = sig.parameters["log_level"]
    assert log_level_param.default == LogLevel.DEBUG
