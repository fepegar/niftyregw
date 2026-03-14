"""CLI command for installing NiftyReg binaries."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from niftyregw.commands import setup_logger
from niftyregw.enums import LogLevel
from niftyregw.install import _DEFAULT_OUTPUT_DIR, download_niftyreg, get_platform


def install(
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to install binaries into. Default: ~/.local/bin.",
        ),
    ] = None,
    show_platform: Annotated[
        bool,
        typer.Option(
            "--platform",
            help="Show the detected platform and exit without installing.",
        ),
    ] = False,
    device: Annotated[
        str,
        typer.Option(
            help="Device: cpu, gpu, cuda, cuda:<id>, or auto (detect CUDA).",
        ),
    ] = "auto",
    log_level: Annotated[
        LogLevel,
        typer.Option(
            "--log",
            case_sensitive=False,
            help="Set the log level.",
            rich_help_panel="Logging",
        ),
    ] = LogLevel.DEBUG,
) -> None:
    """Download and install NiftyReg binaries."""
    setup_logger(log_level)
    install_logger = logger.bind(executable="niftyregw")

    if show_platform:
        platform_name = get_platform(device)
        install_logger.info(f"Platform: {platform_name}")
        return

    out_dir = output_dir if output_dir is not None else _DEFAULT_OUTPUT_DIR
    installed = download_niftyreg(out_dir, device=device)
    for path in installed:
        install_logger.info(f"  Installed {path.name} → {path}")
    install_logger.info(f"Done! {len(installed)} binaries installed.")
