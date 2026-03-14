import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import requests
from loguru import logger

_GITHUB_URL = "https://github.com/KCL-BMEIS/niftyreg/releases/download/v2.0.0/NiftyReg-{name}-v2.0.0.zip"


def is_cuda_available() -> bool:
    """Check whether CUDA is usable by the installed NiftyReg binaries.

    Tries ``reg_gpuinfo`` first (shipped with CUDA-enabled NiftyReg builds).
    Falls back to ``nvidia-smi`` when ``reg_gpuinfo`` is not installed yet
    (e.g. before ``niftyregw install``).
    """
    for cmd in (["reg_gpuinfo"], ["nvidia-smi"]):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            continue
    return False


def _should_use_gpu(device: str) -> bool:
    """Decide whether to enable GPU based on the *device* string.

    Args:
        device: ``"cpu"``, ``"gpu"``, ``"cuda"``, ``"cuda:<id>"`` or
            ``"auto"``.

    Returns:
        ``True`` when GPU should be used.
    """
    if device == "cpu":
        return False
    if device in ("gpu", "cuda") or device.startswith("cuda:"):
        return True
    return is_cuda_available()


def parse_device(device: str) -> tuple[bool, int | None]:
    """Parse a device string into GPU flag and optional GPU id.

    Args:
        device: ``"cpu"``, ``"gpu"``, ``"cuda"``, ``"cuda:<id>"`` or
            ``"auto"``.

    Returns:
        A ``(use_gpu, gpu_id)`` tuple.  *gpu_id* is ``None`` unless the
        caller specified ``"cuda:<id>"``.

    Raises:
        ValueError: If the device string is not recognised.
    """
    device = device.strip().lower()
    if device == "cpu":
        return False, None
    if device in ("gpu", "cuda"):
        return True, None
    if device.startswith("cuda:"):
        try:
            gpu_id = int(device.split(":", 1)[1])
        except ValueError:
            msg = f"Invalid GPU id in device string: {device!r}"
            raise ValueError(msg) from None
        return True, gpu_id
    if device == "auto":
        return is_cuda_available(), None
    msg = f"Unknown device: {device!r}. Use cpu, gpu, cuda, cuda:<id> or auto."
    raise ValueError(msg)


def get_platform(device: str = "auto") -> str:
    """Get the detected platform name for NiftyReg binary selection.

    Args:
        device: ``"cpu"``, ``"gpu"`` or ``"auto"`` (default).  When
            ``"cpu"`` the CUDA variant is never selected; when ``"gpu"``
            the CUDA variant is always selected (on supported OSes).

    Returns:
        Platform name string, one of: "Ubuntu", "Ubuntu-CUDA", "macOS",
        "macOS-Intel", "Windows", or "Windows-CUDA".
    """
    system = platform.system()
    use_gpu = _should_use_gpu(device)
    match system:
        case "Linux":
            platform_name = "Ubuntu-CUDA" if use_gpu else "Ubuntu"
        case "Darwin":
            is_intel = platform.processor() == "i386" or platform.processor() == "i686"
            platform_name = "macOS-Intel" if is_intel else "macOS"
        case "Windows":
            platform_name = "Windows-CUDA" if use_gpu else "Windows"
        case _:
            raise Exception(f"Unsupported platform: {system}")
    return platform_name


def _get_download_url(device: str = "auto") -> str:
    platform_name = get_platform(device)
    return _GITHUB_URL.format(name=platform_name)


_DEFAULT_OUTPUT_DIR = Path.home() / ".local" / "bin"


def download_niftyreg(
    out_dir: Path = _DEFAULT_OUTPUT_DIR,
    device: str = "auto",
) -> list[Path]:
    """Download NiftyReg binaries and install them to *out_dir*.

    Args:
        out_dir: Directory where the binaries will be placed.
            Defaults to ``~/.local/bin``.
        device: ``"cpu"``, ``"gpu"`` or ``"auto"`` (default).

    Returns:
        List of paths to the installed binaries.
    """
    url = _get_download_url(device)
    download_logger = logger.bind(executable="niftyregw")
    download_logger.info(f"Downloading from {url}")
    response = requests.get(url)
    if response.status_code != 200:
        msg = f"Failed to download NiftyReg. Status code: {response.status_code}"
        raise RuntimeError(msg)

    zip_path = Path(tempfile.gettempdir(), "NiftyReg.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    out_tmp_dir = Path(tempfile.gettempdir(), "NiftyReg")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(out_tmp_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    for path in out_tmp_dir.rglob("**/reg_*"):
        if not path.is_file():
            continue
        path.chmod(path.stat().st_mode | 0o111)
        dest = out_dir / path.name
        shutil.move(path, dest)
        installed.append(dest)

    # Clean up
    shutil.rmtree(out_tmp_dir, ignore_errors=True)
    zip_path.unlink(missing_ok=True)

    return sorted(installed)


def _which(program: str) -> Path | None:
    path = shutil.which(program)
    return Path(path) if path else None


BINARIES = (
    "reg_aladin",
    "reg_average",
    "reg_f3d",
    "reg_jacobian",
    "reg_measure",
    "reg_resample",
    "reg_tools",
    "reg_transform",
)


def find(tool: str) -> Path | None:
    """Find a NiftyReg binary by name (e.g. ``"reg_aladin"``)."""
    return _which(tool)


def aladin() -> Path | None:
    return find("reg_aladin")
