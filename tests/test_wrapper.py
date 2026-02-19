"""Tests for niftyregw.wrapper module."""

import subprocess
from pathlib import Path
from subprocess import PIPE
from unittest.mock import MagicMock, Mock, patch

import pytest
from loguru import logger

from niftyregw import wrapper


def test_get_path_found():
    """Test _get_path when tool is found."""
    with patch.object(wrapper, "_find", return_value=Path("/usr/bin/reg_aladin")):
        result = wrapper._get_path("reg_aladin")
        assert result == Path("/usr/bin/reg_aladin")


def test_get_path_not_found():
    """Test _get_path when tool is not found."""
    with patch.object(wrapper, "_find", return_value=None):
        with pytest.raises(FileNotFoundError, match="reg_aladin not found"):
            wrapper._get_path("reg_aladin")


def test_run_basic(temp_dir):
    """Test basic run function without logger."""
    tool_path = temp_dir / "reg_aladin"

    mock_process = Mock()
    mock_process.stdout = iter(["output line 1\n", "output line 2\n"])
    mock_process.stderr = iter(["[NiftyReg] Starting\n"])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process),
        patch("builtins.print") as mock_print,
    ):
        wrapper.run("reg_aladin", "-ref", "ref.nii")
        assert mock_print.called


def test_run_with_logger(temp_dir):
    """Test run function with logger."""
    tool_path = temp_dir / "reg_aladin"

    mock_process = Mock()
    mock_process.stdout = iter(["output line\n"])
    mock_process.stderr = iter(["[NiftyReg WARNING] warning message\n"])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    test_logger = logger.bind(executable="test")

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process),
        patch.object(test_logger, "warning") as mock_warning,
    ):
        wrapper.run("reg_aladin", "-ref", "ref.nii", tool_logger=test_logger)
        mock_warning.assert_called_once_with("[NiftyReg WARNING] warning message")


def test_run_strips_backslashes_and_newlines():
    """Test run strips backslashes and newlines from arguments."""
    tool_path = Path("/usr/bin/reg_aladin")

    mock_process = Mock()
    mock_process.stdout = iter([])
    mock_process.stderr = iter([])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process) as mock_popen,
    ):
        wrapper.run("reg_aladin", "-ref\\\n", "ref.nii\\\n")
        # Check that backslashes and newlines were stripped
        call_args = mock_popen.call_args[0][0]
        assert "-ref\\\n" not in call_args
        assert "ref.nii\\\n" not in call_args
        assert "-ref" in call_args
        assert "ref.nii" in call_args


def test_run_filters_empty_args():
    """Test run filters out empty arguments."""
    tool_path = Path("/usr/bin/reg_aladin")

    mock_process = Mock()
    mock_process.stdout = iter([])
    mock_process.stderr = iter([])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process) as mock_popen,
    ):
        wrapper.run("reg_aladin", "-ref", "", "ref.nii")
        call_args = mock_popen.call_args[0][0]
        assert "" not in call_args
        assert "-ref" in call_args
        assert "ref.nii" in call_args


def test_run_handles_error_messages(temp_dir):
    """Test run handles [NiftyReg ERROR] messages."""
    tool_path = temp_dir / "reg_aladin"

    mock_process = Mock()
    mock_process.stdout = iter([])
    mock_process.stderr = iter(["[NiftyReg ERROR] error message\n"])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    test_logger = logger.bind(executable="test")

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process),
        patch.object(test_logger, "error") as mock_error,
    ):
        wrapper.run("reg_aladin", tool_logger=test_logger)
        mock_error.assert_called_once_with("[NiftyReg ERROR] error message")


def test_run_handles_info_messages(temp_dir):
    """Test run handles regular info messages."""
    tool_path = temp_dir / "reg_aladin"

    mock_process = Mock()
    mock_process.stdout = iter([])
    mock_process.stderr = iter(["Regular info message\n"])
    mock_process.__enter__ = Mock(return_value=mock_process)
    mock_process.__exit__ = Mock(return_value=False)

    test_logger = logger.bind(executable="test")

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch("niftyregw.wrapper.Popen", return_value=mock_process),
        patch.object(test_logger, "info") as mock_info,
    ):
        wrapper.run("reg_aladin", tool_logger=test_logger)
        mock_info.assert_called_once_with("Regular info message")


def test_reg_aladin_minimal(temp_dir):
    """Test reg_aladin with minimal required parameters."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    with (
        patch.object(wrapper, "_run_with_logging") as mock_run,
    ):
        wrapper.reg_aladin(ref_path, flo_path)
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[0] == "reg_aladin"
        assert any("ref.nii" in arg for arg in args)
        assert any("flo.nii" in arg for arg in args)


def test_reg_aladin_with_output_affine(temp_dir):
    """Test reg_aladin with output_affine parameter."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    aff_path = temp_dir / "output.txt"
    ref_path.touch()
    flo_path.touch()

    with (
        patch.object(wrapper, "_run_with_logging") as mock_run,
    ):
        wrapper.reg_aladin(ref_path, flo_path, output_affine=aff_path)
        args = mock_run.call_args[0]
        assert any("output.txt" in arg for arg in args)


def test_reg_aladin_cleanup_default_file(temp_dir):
    """Test reg_aladin cleans up default output file when not requested."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    # Simulate creating the default file during registration
    def create_default_file(*args, **kwargs):
        (Path.cwd() / "outputAffine.txt").touch()

    with (
        patch.object(wrapper, "_run_with_logging", side_effect=create_default_file),
    ):
        # Ensure default file doesn't exist before
        default_file = Path.cwd() / "outputAffine.txt"
        if default_file.exists():
            default_file.unlink()

        wrapper.reg_aladin(ref_path, flo_path)

        # File should be cleaned up
        assert not default_file.exists()


def test_reg_aladin_keeps_default_file_if_requested(temp_dir):
    """Test reg_aladin keeps default output file when explicitly requested."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    default_file = Path.cwd() / "outputAffine.txt"

    # Simulate creating the default file during registration
    def create_default_file(*args, **kwargs):
        default_file.touch()

    with (
        patch.object(wrapper, "_run_with_logging", side_effect=create_default_file),
    ):
        # Clean up before test
        if default_file.exists():
            default_file.unlink()

        wrapper.reg_aladin(ref_path, flo_path, output_affine=default_file)

        # File should still exist
        assert default_file.exists()

        # Clean up after test
        default_file.unlink()


def test_reg_aladin_handles_existing_default_file(temp_dir):
    """Test reg_aladin doesn't clean up pre-existing default file."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    default_file = Path.cwd() / "outputAffine.txt"
    default_file.write_text("existing content")

    with (
        patch.object(wrapper, "_run_with_logging"),
    ):
        wrapper.reg_aladin(ref_path, flo_path)
        # Pre-existing file should not be deleted
        assert default_file.exists()
        assert default_file.read_text() == "existing content"

    # Clean up
    default_file.unlink()


def test_reg_aladin_all_boolean_flags(temp_dir):
    """Test reg_aladin with all boolean flags enabled."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    with patch.object(wrapper, "_run_with_logging") as mock_run:
        wrapper.reg_aladin(
            ref_path,
            flo_path,
            no_symmetric=True,
            rigid_only=True,
            affine_direct=True,
            use_nifti_origin=True,
            use_masks_centre_of_mass=True,
            use_images_centre_of_mass=True,
            isotropic=True,
            block_step_size_2=True,
            verbose_off=True,
        )
        args = " ".join(mock_run.call_args[0])
        assert "-noSym" in args
        assert "-rigOnly" in args
        assert "-affDirect" in args
        assert "-nac" in args
        assert "-comm" in args
        assert "-comi" in args
        assert "-iso" in args
        assert "-speeeeed" in args
        assert "-voff" in args


def test_reg_aladin_all_numeric_params(temp_dir):
    """Test reg_aladin with all numeric parameters."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_path.touch()
    flo_path.touch()

    with patch.object(wrapper, "_run_with_logging") as mock_run:
        wrapper.reg_aladin(
            ref_path,
            flo_path,
            max_iterations=10,
            num_levels=4,
            num_levels_to_perform=3,
            smooth_reference=1.5,
            smooth_floating=2.0,
            reference_lower_threshold=0.1,
            reference_upper_threshold=0.9,
            floating_lower_threshold=0.2,
            floating_upper_threshold=0.8,
            padding=0.0,
            interpolation=1,
            percent_blocks_to_use=75,
            percent_inliers=80,
            omp_threads=4,
        )
        args = " ".join(mock_run.call_args[0])
        assert "-maxit 10" in args
        assert "-ln 4" in args
        assert "-lp 3" in args
        assert "-smooR 1.5" in args
        assert "-smooF 2.0" in args


def test_reg_aladin_with_masks(temp_dir):
    """Test reg_aladin with mask parameters."""
    ref_path = temp_dir / "ref.nii"
    flo_path = temp_dir / "flo.nii"
    ref_mask = temp_dir / "ref_mask.nii"
    flo_mask = temp_dir / "flo_mask.nii"
    ref_path.touch()
    flo_path.touch()
    ref_mask.touch()
    flo_mask.touch()

    with patch.object(wrapper, "_run_with_logging") as mock_run:
        wrapper.reg_aladin(
            ref_path, flo_path, reference_mask=ref_mask, floating_mask=flo_mask
        )
        args = " ".join(mock_run.call_args[0])
        assert "-rmask" in args
        assert "-fmask" in args


def test_run_with_logging(temp_dir):
    """Test _run_with_logging function."""
    tool_path = temp_dir / "reg_aladin"
    tool_path.touch()

    with (
        patch.object(wrapper, "_get_path", return_value=tool_path),
        patch.object(wrapper, "run") as mock_run,
    ):
        wrapper._run_with_logging("reg_aladin", "-ref ref.nii \\", "-flo flo.nii \\")
        mock_run.assert_called_once()
        # Check that arguments were properly parsed
        args = mock_run.call_args[0]
        assert "reg_aladin" in args


def test_format_matrix_line_basic():
    """Test basic matrix line formatting with mixed precision."""
    line = "0.953207  0.0293464       0.0196046       3.7271"
    result = wrapper._format_matrix_line(line)
    # Should format to 3 decimal places and align
    assert "0.953" in result
    assert "0.029" in result
    assert "0.020" in result
    assert "3.727" in result


def test_format_matrix_line_with_negative():
    """Test matrix line formatting with negative numbers."""
    line = "0.00319424        0.974996        -0.226491       5.05835"
    result = wrapper._format_matrix_line(line)
    assert "0.003" in result
    assert "0.975" in result
    assert "-0.226" in result
    assert "5.058" in result


def test_format_matrix_line_with_zeros():
    """Test matrix line formatting with zeros."""
    line = "0 0       0       1"
    result = wrapper._format_matrix_line(line)
    # Zeros should remain as "0" without decimal places
    # Check that result has properly formatted zeros and one
    parts = result.split()
    assert "0" in parts
    assert "1" in parts


def test_format_matrix_line_with_integers():
    """Test matrix line formatting preserves integers."""
    line = "1.0 2.0 3.0 4.0"
    result = wrapper._format_matrix_line(line)
    # Should format as integers since they have no fractional part
    parts = result.split()
    assert "1" in parts
    assert "2" in parts
    assert "3" in parts
    assert "4" in parts


def test_format_matrix_line_large_numbers():
    """Test matrix line formatting with numbers >= 10 and >= 100."""
    line = "10.5 20.123 -15.678 100.234"
    result = wrapper._format_matrix_line(line)
    assert "10.500" in result
    assert "20.123" in result
    assert "-15.678" in result
    assert "100.234" in result


def test_format_matrix_line_integer_large_numbers():
    """Test matrix line formatting with large integers."""
    line = "100 200 -300 1000"
    result = wrapper._format_matrix_line(line)
    parts = result.split()
    assert "100" in parts
    assert "200" in parts
    assert "-300" in parts
    assert "1000" in parts


def test_format_matrix_line_not_matrix():
    """Test that non-matrix lines pass through unchanged."""
    # Not 4 numbers
    assert wrapper._format_matrix_line("1 2 3") == "1 2 3"
    assert wrapper._format_matrix_line("1 2 3 4 5") == "1 2 3 4 5"
    
    # Not numbers
    assert wrapper._format_matrix_line("a b c d") == "a b c d"
    
    # Regular text
    line = "This is a regular line"
    assert wrapper._format_matrix_line(line) == line
    
    # Mixed numbers and text
    assert wrapper._format_matrix_line("1 2 three 4") == "1 2 three 4"


def test_format_matrix_line_alignment():
    """Test that matrix lines are properly aligned."""
    # Lines from the issue example
    lines = [
        "0.953207  0.0293464       0.0196046       3.7271",
        "0.00319424        0.974996        -0.226491       5.05835",
        "0.00397915        0.25023 0.886231        1.27031",
        "0 0       0       1",
    ]
    
    results = [wrapper._format_matrix_line(line) for line in lines]
    
    # Each result should start with a space
    for result in results:
        assert result.startswith(" ")
    
    # All results should have 4 number groups separated by two spaces
    for result in results:
        # Strip leading space and split
        parts = result.strip().split()
        assert len(parts) == 4


def test_read_stream_formats_matrices(temp_dir):
    """Test that _read_stream formats matrix lines."""
    mock_stream = iter([
        "Regular output line\n",
        "0.953207  0.0293464  0.0196046  3.7271\n",
        "Another regular line\n",
        "0 0 0 1\n",
    ])
    
    captured_lines = []
    
    def capture_print(line):
        captured_lines.append(line)
    
    with patch("builtins.print", side_effect=capture_print):
        wrapper._read_stream(mock_stream, False, None)
    
    # Check that regular lines pass through
    assert captured_lines[0] == "Regular output line"
    
    # Check that matrix lines are formatted
    assert "0.953" in captured_lines[1]
    assert "0.029" in captured_lines[1]
    
    # Check that another regular line passes through
    assert captured_lines[2] == "Another regular line"
    
    # Check that the last matrix line is formatted
    assert len(captured_lines[3].split()) == 4
