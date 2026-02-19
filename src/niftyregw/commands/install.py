"""CLI command for installing NiftyReg binaries."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from niftyregw.install import _DEFAULT_OUTPUT_DIR, _get_platform, download_niftyreg


def install(
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to install binaries into. Default: ~/.local/bin.",
        ),
    ] = None,
    platform: Annotated[
        bool,
        typer.Option(
            "--platform",
            help="Show the detected platform and exit without installing.",
        ),
    ] = False,
) -> None:
    """Download and install NiftyReg binaries."""
    if platform:
        platform_name = _get_platform()
        typer.echo(f"Platform: {platform_name}")
        return

    out_dir = output_dir if output_dir is not None else _DEFAULT_OUTPUT_DIR
    typer.echo(f"Downloading NiftyReg binaries to {out_dir}...")
    installed = download_niftyreg(out_dir)
    for path in installed:
        typer.echo(f"  Installed {path.name} → {path}")
    typer.echo(f"Done! {len(installed)} binaries installed.")
