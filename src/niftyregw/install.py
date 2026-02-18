import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import requests

_GITHUB_URL = "https://github.com/KCL-BMEIS/niftyreg/releases/download/v2.0.0/NiftyReg-{name}-v2.0.0.zip"


def _is_cuda_available():
    try:
        result = subprocess.run(
            ["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _get_platform():
    system = platform.system()
    has_cuda = _is_cuda_available()
    match system:
        case "Linux":
            platform_name = "Ubuntu-CUDA" if has_cuda else "Ubuntu"
        case "Darwin":
            is_intel = platform.processor() == "i386" or platform.processor() == "i686"
            platform_name = "macOS-Intel" if is_intel else "macOS"
        case "Windows":
            platform_name = "Windows-CUDA" if has_cuda else "Windows"
        case _:
            raise Exception(f"Unsupported platform: {system}")
    return platform_name


def _get_download_url():
    platform_name = _get_platform()
    return _GITHUB_URL.format(name=platform_name)


def _download_niftyreg(out_dir: Path) -> None:
    url = _get_download_url()
    response = requests.get(url)
    if response.status_code == 200:
        zip_path = Path(tempfile.gettempdir(), "NiftyReg.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        out_tmp_dir = Path(tempfile.gettempdir(), "NiftyReg")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(out_tmp_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for path in out_tmp_dir.rglob("**/reg_*"):
            path.chmod(path.stat().st_mode | 0o111)  # chmod +x
            path.rename(out_dir / path.name)
    else:
        msg = f"Failed to download NiftyReg. Status code: {response.status_code}"
        raise RuntimeError(msg)


def _which(program: str) -> Path | None:
    path = shutil.which(program)
    return Path(path) if path else None


def aladin() -> Path | None:
    return _which("reg_aladin")
