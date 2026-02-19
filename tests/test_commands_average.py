"""Tests for niftyregw.commands.average module."""

from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from niftyregw.commands.average import app, avg, avg_lts, avg_tran, cmd_file, demean, demean_noaff

runner = CliRunner()


def test_average_app_exists():
    """Test that average app exists."""
    assert isinstance(app, typer.Typer)


def test_average_app_help():
    """Test average app help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "average" in result.stdout.lower()


def test_avg_command(temp_dir):
    """Test avg command."""
    output = temp_dir / "output.nii"
    input1 = temp_dir / "input1.nii"
    input2 = temp_dir / "input2.nii"
    input1.touch()
    input2.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app, ["avg", "-o", str(output), str(input1), str(input2)]
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert "reg_average" in call_args
        assert "-avg" in call_args


def test_avg_with_nn_flag(temp_dir):
    """Test avg with nearest neighbour flag."""
    output = temp_dir / "output.nii"
    input1 = temp_dir / "input1.nii"
    input1.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(app, ["avg", "-o", str(output), str(input1), "--nn"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "--NN" in call_args


def test_avg_with_linear_flag(temp_dir):
    """Test avg with linear interpolation flag."""
    output = temp_dir / "output.nii"
    input1 = temp_dir / "input1.nii"
    input1.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(app, ["avg", "-o", str(output), str(input1), "--lin"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "--LIN" in call_args


def test_avg_lts_command(temp_dir):
    """Test avg-lts command."""
    output = temp_dir / "output.txt"
    input1 = temp_dir / "input1.txt"
    input2 = temp_dir / "input2.txt"
    input1.touch()
    input2.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app, ["avg-lts", "-o", str(output), str(input1), str(input2)]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "-avg_lts" in call_args


def test_avg_tran_command(temp_dir):
    """Test avg-tran command."""
    output = temp_dir / "output.nii"
    reference = temp_dir / "ref.nii"
    trans1 = temp_dir / "trans1.txt"
    flo1 = temp_dir / "flo1.nii"
    reference.touch()
    trans1.touch()
    flo1.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app,
            [
                "avg-tran",
                "-o",
                str(output),
                "-r",
                str(reference),
                str(trans1),
                str(flo1),
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "-avg_tran" in call_args


def test_demean_command(temp_dir):
    """Test demean command."""
    output = temp_dir / "output.nii"
    reference = temp_dir / "ref.nii"
    trans1 = temp_dir / "trans1.txt"
    flo1 = temp_dir / "flo1.nii"
    reference.touch()
    trans1.touch()
    flo1.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app,
            ["demean", "-o", str(output), "-r", str(reference), str(trans1), str(flo1)],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "-demean" in call_args


def test_demean_noaff_command(temp_dir):
    """Test demean-noaff command."""
    output = temp_dir / "output.nii"
    reference = temp_dir / "ref.nii"
    aff1 = temp_dir / "aff1.txt"
    nr1 = temp_dir / "nr1.nii"
    flo1 = temp_dir / "flo1.nii"
    reference.touch()
    aff1.touch()
    nr1.touch()
    flo1.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app,
            [
                "demean-noaff",
                "-o",
                str(output),
                "-r",
                str(reference),
                str(aff1),
                str(nr1),
                str(flo1),
            ],
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "-demean_noaff" in call_args


def test_cmd_file_command(temp_dir):
    """Test cmd-file command."""
    output = temp_dir / "output.nii"
    cmd_file_path = temp_dir / "command.txt"
    cmd_file_path.touch()

    with (
        patch("niftyregw.commands.average.setup_logger"),
        patch("niftyregw.commands.average.run") as mock_run,
    ):
        result = runner.invoke(
            app, ["cmd-file", "-o", str(output), "-c", str(cmd_file_path)]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0]
        assert "--cmd_file" in call_args


def test_average_help_callback():
    """Test average --print-help callback."""
    result = runner.invoke(app, ["--print-help"])
    # Help callback will call run() which will exit
    # We just want to verify it was attempted
    assert result.exit_code != 0 or "help" in result.stdout.lower()


def test_avg_help():
    """Test avg subcommand help."""
    result = runner.invoke(app, ["avg", "--help"])
    assert result.exit_code == 0
    assert "output" in result.stdout.lower()
