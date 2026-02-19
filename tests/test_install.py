"""Tests for niftyregw.install module."""

import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import requests

from niftyregw import install


def test_is_cuda_available_true():
    """Test _is_cuda_available when nvidia-smi is available."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)
        assert install._is_cuda_available() is True
        mock_run.assert_called_once_with(
            ["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


def test_is_cuda_available_false():
    """Test _is_cuda_available when nvidia-smi returns non-zero."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=1)
        assert install._is_cuda_available() is False


def test_is_cuda_available_not_found():
    """Test _is_cuda_available when nvidia-smi is not found."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert install._is_cuda_available() is False


def test_get_platform_linux_no_cuda():
    """Test _get_platform for Linux without CUDA."""
    with (
        patch("platform.system", return_value="Linux"),
        patch.object(install, "_is_cuda_available", return_value=False),
    ):
        assert install._get_platform() == "Ubuntu"


def test_get_platform_linux_with_cuda():
    """Test _get_platform for Linux with CUDA."""
    with (
        patch("platform.system", return_value="Linux"),
        patch.object(install, "_is_cuda_available", return_value=True),
    ):
        assert install._get_platform() == "Ubuntu-CUDA"


def test_get_platform_macos_intel():
    """Test _get_platform for macOS on Intel."""
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.processor", return_value="i386"),
        patch.object(install, "_is_cuda_available", return_value=False),
    ):
        assert install._get_platform() == "macOS-Intel"


def test_get_platform_macos_arm():
    """Test _get_platform for macOS on ARM."""
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.processor", return_value="arm"),
        patch.object(install, "_is_cuda_available", return_value=False),
    ):
        assert install._get_platform() == "macOS"


def test_get_platform_windows_no_cuda():
    """Test _get_platform for Windows without CUDA."""
    with (
        patch("platform.system", return_value="Windows"),
        patch.object(install, "_is_cuda_available", return_value=False),
    ):
        assert install._get_platform() == "Windows"


def test_get_platform_windows_with_cuda():
    """Test _get_platform for Windows with CUDA."""
    with (
        patch("platform.system", return_value="Windows"),
        patch.object(install, "_is_cuda_available", return_value=True),
    ):
        assert install._get_platform() == "Windows-CUDA"


def test_get_platform_unsupported():
    """Test _get_platform for unsupported platform."""
    with (
        patch("platform.system", return_value="FreeBSD"),
        patch.object(install, "_is_cuda_available", return_value=False),
    ):
        with pytest.raises(Exception, match="Unsupported platform: FreeBSD"):
            install._get_platform()


def test_get_download_url():
    """Test _get_download_url returns correct URL."""
    with patch.object(install, "_get_platform", return_value="Ubuntu"):
        url = install._get_download_url()
        assert (
            url
            == "https://github.com/KCL-BMEIS/niftyreg/releases/download/v2.0.0/NiftyReg-Ubuntu-v2.0.0.zip"
        )


def test_download_niftyreg_success(temp_dir):
    """Test successful download_niftyreg."""
    # Create a mock zip file with reg_aladin
    zip_path = temp_dir / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Add a mock binary
        zf.writestr("NiftyReg/bin/reg_aladin", "fake binary content")

    # Mock the download
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = zip_path.read_bytes()

    with (
        patch("requests.get", return_value=mock_response),
        patch.object(install, "_get_download_url", return_value="http://test.url"),
        patch("tempfile.gettempdir", return_value=str(temp_dir)),
    ):
        out_dir = temp_dir / "output"
        result = install.download_niftyreg(out_dir)

        assert len(result) == 1
        assert result[0].name == "reg_aladin"
        assert result[0].parent == out_dir
        assert result[0].exists()


def test_download_niftyreg_failure():
    """Test download_niftyreg with failed download."""
    mock_response = Mock()
    mock_response.status_code = 404

    with (
        patch("requests.get", return_value=mock_response),
        patch.object(install, "_get_download_url", return_value="http://test.url"),
    ):
        with pytest.raises(
            RuntimeError, match="Failed to download NiftyReg. Status code: 404"
        ):
            install.download_niftyreg()


def test_which_found():
    """Test _which when program is found."""
    with patch("shutil.which", return_value="/usr/bin/test"):
        result = install._which("test")
        assert result == Path("/usr/bin/test")


def test_which_not_found():
    """Test _which when program is not found."""
    with patch("shutil.which", return_value=None):
        result = install._which("nonexistent")
        assert result is None


def test_binaries_constant():
    """Test BINARIES constant has expected values."""
    expected = (
        "reg_aladin",
        "reg_average",
        "reg_f3d",
        "reg_jacobian",
        "reg_measure",
        "reg_resample",
        "reg_tools",
        "reg_transform",
    )
    assert install.BINARIES == expected


def test_find_tool_found():
    """Test find when tool is found."""
    with patch("shutil.which", return_value="/usr/bin/reg_aladin"):
        result = install.find("reg_aladin")
        assert result == Path("/usr/bin/reg_aladin")


def test_find_tool_not_found():
    """Test find when tool is not found."""
    with patch("shutil.which", return_value=None):
        result = install.find("reg_aladin")
        assert result is None


def test_aladin_helper():
    """Test aladin() helper function."""
    with patch("shutil.which", return_value="/usr/bin/reg_aladin"):
        result = install.aladin()
        assert result == Path("/usr/bin/reg_aladin")


def test_default_output_dir():
    """Test _DEFAULT_OUTPUT_DIR is set correctly."""
    expected = Path.home() / ".local" / "bin"
    assert install._DEFAULT_OUTPUT_DIR == expected


def test_download_niftyreg_creates_directory(temp_dir):
    """Test download_niftyreg creates output directory if it doesn't exist."""
    # Create a mock zip file
    zip_path = temp_dir / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("NiftyReg/bin/reg_aladin", "fake binary")

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = zip_path.read_bytes()

    with (
        patch("requests.get", return_value=mock_response),
        patch.object(install, "_get_download_url", return_value="http://test.url"),
        patch("tempfile.gettempdir", return_value=str(temp_dir)),
    ):
        out_dir = temp_dir / "new" / "directory"
        assert not out_dir.exists()
        result = install.download_niftyreg(out_dir)
        assert out_dir.exists()
        assert len(result) > 0
