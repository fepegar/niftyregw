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
        patch.object(logger, "info") as mock_info,
    ):
        wrapper.run("reg_aladin", "-ref", "ref.nii")
        assert mock_info.called


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
