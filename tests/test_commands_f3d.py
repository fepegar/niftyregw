"""Tests for niftyregw.commands.f3d module."""

from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from niftyregw.commands.f3d import f3d

runner = CliRunner()


def test_f3d_minimal_args(mock_nifti_image, temp_dir):
    """Test f3d with minimal required arguments."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(app, ["-r", str(ref_img), "-f", str(flo_img)])

        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_f3d_landmarks_validation(mock_nifti_image, temp_dir):
    """Test f3d validates landmarks weight and file together."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run"),
    ):
        app = typer.Typer()
        app.command()(f3d)

        # Only weight, no file
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "--landmarks-weight", "0.5"]
        )
        assert result.exit_code == 1
        assert "must be provided together" in result.stdout


def test_f3d_with_spline_options(mock_nifti_image, temp_dir):
    """Test f3d with spline spacing options."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--spacing-x",
                "5.0",
                "--spacing-y",
                "5.0",
                "--spacing-z",
                "5.0",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-sx 5.0" in args_str
        assert "-sy 5.0" in args_str
        assert "-sz 5.0" in args_str


def test_f3d_with_regularisation(mock_nifti_image, temp_dir):
    """Test f3d with regularisation parameters."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--bending-energy",
                "0.01",
                "--linear-energy",
                "0.02",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-be 0.01" in args_str
        assert "-le 0.02" in args_str


def test_f3d_with_similarity_measures(mock_nifti_image, temp_dir):
    """Test f3d with similarity measure options."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--use-nmi",
                "--use-ssd",
                "--use-kld",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "--nmi" in args_str
        assert "--ssd" in args_str
        assert "--kld" in args_str


def test_f3d_help():
    """Test f3d --help."""
    app = typer.Typer()
    app.command()(f3d)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "reference" in result.stdout.lower()


def test_f3d_version_callback():
    """Test f3d --version callback."""
    with patch("niftyregw.wrapper.run") as mock_run:
        from niftyregw.commands.f3d import _version_callback

        try:
            _version_callback(True)
        except typer.Exit:
            pass
        mock_run.assert_called_once_with("reg_f3d", "--version")


def test_f3d_help_callback():
    """Test f3d --print-help callback."""
    with patch("niftyregw.wrapper.run") as mock_run:
        from niftyregw.commands.f3d import _help_callback

        try:
            _help_callback(True)
        except typer.Exit:
            pass
        mock_run.assert_called_once_with("reg_f3d", "-h")


def test_f3d_with_masks(mock_nifti_image, temp_dir):
    """Test f3d with mask images."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    ref_mask = temp_dir / "ref_mask.nii.gz"
    flo_mask = temp_dir / "flo_mask.nii.gz"
    flo_img.touch()
    ref_mask.touch()
    flo_mask.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "-m",
                str(ref_mask),
                "--floating-mask",
                str(flo_mask),
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert str(ref_mask) in args_str
        assert str(flo_mask) in args_str


def test_f3d_with_optimisation_params(mock_nifti_image, temp_dir):
    """Test f3d with optimisation parameters."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.f3d.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(f3d)
        result = runner.invoke(
            app,
            [
                "-r",
                str(ref_img),
                "-f",
                str(flo_img),
                "--max-iterations",
                "200",
                "--num-levels",
                "4",
                "--no-pyramid",
                "--no-conjugate-gradient",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-maxit 200" in args_str
        assert "-ln 4" in args_str
        assert "-nopy" in args_str
        assert "-noConj" in args_str
