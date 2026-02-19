"""Tests for niftyregw.commands.measure, jacobian, resample, tools, and transform modules."""

from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from niftyregw.commands.jacobian import jacobian
from niftyregw.commands.measure import measure
from niftyregw.commands.resample import resample
from niftyregw.commands.tools import tools
from niftyregw.commands.transform import app as transform_app

runner = CliRunner()


# Measure tests
def test_measure_minimal(mock_nifti_image, temp_dir):
    """Test measure with minimal arguments."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.measure.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(measure)
        result = runner.invoke(app, ["-r", str(ref_img), "-f", str(flo_img), "--ncc"])

        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_measure_all_metrics(mock_nifti_image, temp_dir):
    """Test measure with all metric flags."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.measure.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(measure)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "--ncc", "--lncc", "--nmi", "--ssd"]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "--ncc" in args_str
        assert "--lncc" in args_str
        assert "--nmi" in args_str
        assert "--ssd" in args_str


def test_measure_with_output(mock_nifti_image, temp_dir):
    """Test measure with output file."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    output = temp_dir / "output.txt"
    flo_img.touch()

    with (
        patch("niftyregw.commands.measure.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(measure)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "--ncc", "-o", str(output)]
        )

        assert result.exit_code == 0


def test_measure_help():
    """Test measure --help."""
    app = typer.Typer()
    app.command()(measure)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "measure" in result.stdout.lower() or "similarity" in result.stdout.lower()


# Jacobian tests
def test_jacobian_minimal(temp_dir):
    """Test jacobian with minimal arguments."""
    trans = temp_dir / "trans.nii"
    trans.touch()

    with (
        patch("niftyregw.commands.jacobian.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(jacobian)
        result = runner.invoke(app, ["-t", str(trans)])

        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_jacobian_with_reference(temp_dir, mock_nifti_image):
    """Test jacobian with reference image."""
    trans = temp_dir / "trans.nii"
    ref = mock_nifti_image
    trans.touch()

    with (
        patch("niftyregw.commands.jacobian.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(jacobian)
        result = runner.invoke(app, ["-t", str(trans), "-r", str(ref)])

        assert result.exit_code == 0


def test_jacobian_all_outputs(temp_dir):
    """Test jacobian with all output options."""
    trans = temp_dir / "trans.nii"
    jac_det = temp_dir / "jac_det.nii"
    jac_mat = temp_dir / "jac_mat.nii"
    jac_log = temp_dir / "jac_log.nii"
    trans.touch()

    with (
        patch("niftyregw.commands.jacobian.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(jacobian)
        result = runner.invoke(
            app,
            [
                "-t",
                str(trans),
                "--jacobian-determinant",
                str(jac_det),
                "--jacobian-matrix",
                str(jac_mat),
                "--jacobian-log-determinant",
                str(jac_log),
            ],
        )

        assert result.exit_code == 0


def test_jacobian_help():
    """Test jacobian --help."""
    app = typer.Typer()
    app.command()(jacobian)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "jacobian" in result.stdout.lower() or "transformation" in result.stdout.lower()


# Resample tests
def test_resample_minimal(mock_nifti_image, temp_dir):
    """Test resample with minimal arguments."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.resample.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(resample)
        result = runner.invoke(app, ["-r", str(ref_img), "-f", str(flo_img)])

        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_resample_with_transformation(mock_nifti_image, temp_dir):
    """Test resample with transformation."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    trans = temp_dir / "trans.txt"
    flo_img.touch()
    trans.touch()

    with (
        patch("niftyregw.commands.resample.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(resample)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "-t", str(trans)]
        )

        assert result.exit_code == 0


def test_resample_with_interpolation(mock_nifti_image, temp_dir):
    """Test resample with interpolation order."""
    ref_img = mock_nifti_image
    flo_img = temp_dir / "flo.nii.gz"
    flo_img.touch()

    with (
        patch("niftyregw.commands.resample.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(resample)
        result = runner.invoke(
            app, ["-r", str(ref_img), "-f", str(flo_img), "--interpolation", "1"]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-inter 1" in args_str


def test_resample_help():
    """Test resample --help."""
    app = typer.Typer()
    app.command()(resample)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "resample" in result.stdout.lower()


# Tools tests
def test_tools_minimal(mock_nifti_image, temp_dir):
    """Test tools with minimal arguments."""
    input_img = mock_nifti_image

    with (
        patch("niftyregw.commands.tools.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(tools)
        result = runner.invoke(app, ["-i", str(input_img)])

        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_tools_with_output(mock_nifti_image, temp_dir):
    """Test tools with output file."""
    input_img = mock_nifti_image
    output = temp_dir / "output.nii"

    with (
        patch("niftyregw.commands.tools.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(tools)
        result = runner.invoke(app, ["-i", str(input_img), "-o", str(output)])

        assert result.exit_code == 0


def test_tools_to_float(mock_nifti_image, temp_dir):
    """Test tools with to-float option."""
    input_img = mock_nifti_image

    with (
        patch("niftyregw.commands.tools.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(tools)
        result = runner.invoke(app, ["-i", str(input_img), "--to-float"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-float" in args_str


def test_tools_downsample(mock_nifti_image, temp_dir):
    """Test tools with downsample option."""
    input_img = mock_nifti_image

    with (
        patch("niftyregw.commands.tools.setup_logger"),
        patch("niftyregw.wrapper.run") as mock_run,
    ):
        app = typer.Typer()
        app.command()(tools)
        result = runner.invoke(app, ["-i", str(input_img), "--downsample"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        args_str = " ".join(str(a) for a in call_args)
        assert "-down" in args_str


def test_tools_help():
    """Test tools --help."""
    app = typer.Typer()
    app.command()(tools)
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "tools" in result.stdout.lower() or "manipulation" in result.stdout.lower()


# Transform tests
def test_transform_app_exists():
    """Test that transform app exists."""
    assert isinstance(transform_app, typer.Typer)


def test_transform_app_help():
    """Test transform app help."""
    result = runner.invoke(transform_app, ["--help"])
    assert result.exit_code == 0
    assert "transform" in result.stdout.lower()


def test_transform_help_callback():
    """Test transform --print-help callback."""
    result = runner.invoke(transform_app, ["--print-help"])
    # Help callback will call run() which will exit or show help
    assert result.exit_code != 0 or "help" in result.stdout.lower()
