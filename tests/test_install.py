"""Tests for niftyregw.install module."""

import subprocess
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from niftyregw import install


def testis_cuda_available_via_reg_gpuinfo():
    """Test is_cuda_available when reg_gpuinfo succeeds."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)
        assert install.is_cuda_available() is True
        mock_run.assert_called_once_with(
            ["reg_gpuinfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


def testis_cuda_available_via_nvidia_smi():
    """Test is_cuda_available falls back to nvidia-smi."""

    def _side_effect(cmd, **kwargs):
        if cmd == ["reg_gpuinfo"]:
            raise FileNotFoundError
        return Mock(returncode=0)

    with patch("subprocess.run", side_effect=_side_effect):
        assert install.is_cuda_available() is True


def testis_cuda_available_false():
    """Test is_cuda_available when both commands fail."""
    with patch("subprocess.run", return_value=Mock(returncode=1)):
        assert install.is_cuda_available() is False


def testis_cuda_available_not_found():
    """Test is_cuda_available when neither command is found."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert install.is_cuda_available() is False


def testget_platform_linux_no_cuda():
    """Test get_platform for Linux without CUDA."""
    with (
        patch("platform.system", return_value="Linux"),
        patch.object(install, "is_cuda_available", return_value=False),
    ):
        assert install.get_platform() == "Ubuntu"


def testget_platform_linux_with_cuda():
    """Test get_platform for Linux with CUDA."""
    with (
        patch("platform.system", return_value="Linux"),
        patch.object(install, "is_cuda_available", return_value=True),
    ):
        assert install.get_platform() == "Ubuntu-CUDA"


def testget_platform_macos_intel():
    """Test get_platform for macOS on Intel."""
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.processor", return_value="i386"),
        patch.object(install, "is_cuda_available", return_value=False),
    ):
        assert install.get_platform() == "macOS-Intel"


def testget_platform_macos_arm():
    """Test get_platform for macOS on ARM."""
    with (
        patch("platform.system", return_value="Darwin"),
        patch("platform.processor", return_value="arm"),
        patch.object(install, "is_cuda_available", return_value=False),
    ):
        assert install.get_platform() == "macOS"


def testget_platform_windows_no_cuda():
    """Test get_platform for Windows without CUDA."""
    with (
        patch("platform.system", return_value="Windows"),
        patch.object(install, "is_cuda_available", return_value=False),
    ):
        assert install.get_platform() == "Windows"


def testget_platform_windows_with_cuda():
    """Test get_platform for Windows with CUDA."""
    with (
        patch("platform.system", return_value="Windows"),
        patch.object(install, "is_cuda_available", return_value=True),
    ):
        assert install.get_platform() == "Windows-CUDA"


def testget_platform_unsupported():
    """Test get_platform for unsupported platform."""
    with (
        patch("platform.system", return_value="FreeBSD"),
        patch.object(install, "is_cuda_available", return_value=False),
    ):
        with pytest.raises(Exception, match="Unsupported platform: FreeBSD"):
            install.get_platform()


def testget_download_url():
    """Test get_download_url returns correct URL."""
    with patch.object(install, "get_platform", return_value="Ubuntu"):
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


def testwhich_found():
    """Test which when program is found."""
    with patch("shutil.which", return_value="/usr/bin/test"):
        result = install._which("test")
        assert result == Path("/usr/bin/test")


def testwhich_not_found():
    """Test which when program is not found."""
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


def test_should_use_gpu_cpu():
    """Test _should_use_gpu returns False for cpu."""
    assert install._should_use_gpu("cpu") is False


def test_should_use_gpu_gpu():
    """Test _should_use_gpu returns True for gpu."""
    assert install._should_use_gpu("gpu") is True


def test_should_use_gpu_cuda():
    """Test _should_use_gpu returns True for cuda."""
    assert install._should_use_gpu("cuda") is True


def test_should_use_gpu_cuda_with_id():
    """Test _should_use_gpu returns True for cuda:<id>."""
    assert install._should_use_gpu("cuda:2") is True


def test_should_use_gpu_auto_with_cuda():
    """Test _should_use_gpu returns True for auto when CUDA is available."""
    with patch.object(install, "is_cuda_available", return_value=True):
        assert install._should_use_gpu("auto") is True


def test_should_use_gpu_auto_without_cuda():
    """Test _should_use_gpu returns False for auto when CUDA is unavailable."""
    with patch.object(install, "is_cuda_available", return_value=False):
        assert install._should_use_gpu("auto") is False


def test_parse_device_cpu():
    """Test parse_device for cpu."""
    use_gpu, gpu_id = install.parse_device("cpu")
    assert use_gpu is False
    assert gpu_id is None


def test_parse_device_gpu():
    """Test parse_device for gpu."""
    use_gpu, gpu_id = install.parse_device("gpu")
    assert use_gpu is True
    assert gpu_id is None


def test_parse_device_cuda():
    """Test parse_device for cuda."""
    use_gpu, gpu_id = install.parse_device("cuda")
    assert use_gpu is True
    assert gpu_id is None


def test_parse_device_cuda_with_id():
    """Test parse_device for cuda:<id>."""
    use_gpu, gpu_id = install.parse_device("cuda:2")
    assert use_gpu is True
    assert gpu_id == 2


def test_parse_device_cuda_with_id_zero():
    """Test parse_device for cuda:0."""
    use_gpu, gpu_id = install.parse_device("cuda:0")
    assert use_gpu is True
    assert gpu_id == 0


def test_parse_device_auto_with_cuda():
    """Test parse_device for auto when CUDA is available."""
    with patch.object(install, "is_cuda_available", return_value=True):
        use_gpu, gpu_id = install.parse_device("auto")
        assert use_gpu is True
        assert gpu_id is None


def test_parse_device_auto_without_cuda():
    """Test parse_device for auto when CUDA is unavailable."""
    with patch.object(install, "is_cuda_available", return_value=False):
        use_gpu, gpu_id = install.parse_device("auto")
        assert use_gpu is False
        assert gpu_id is None


def test_parse_device_invalid():
    """Test parse_device raises ValueError for invalid device."""
    with pytest.raises(ValueError, match="Unknown device"):
        install.parse_device("tpu")


def test_parse_device_invalid_cuda_id():
    """Test parse_device raises ValueError for invalid cuda id."""
    with pytest.raises(ValueError, match="Invalid GPU id"):
        install.parse_device("cuda:abc")
