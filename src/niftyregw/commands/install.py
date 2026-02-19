"""CLI command for installing NiftyReg binaries."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from niftyregw.install import _DEFAULT_OUTPUT_DIR, download_niftyreg


def install(
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to install binaries into. Default: ~/.local/bin.",
        ),
    ] = None,
) -> None:
    """Download and install NiftyReg binaries."""
    out_dir = output_dir if output_dir is not None else _DEFAULT_OUTPUT_DIR
    typer.echo(f"Downloading NiftyReg binaries to {out_dir}...")
    installed = download_niftyreg(out_dir)
    for path in installed:
        typer.echo(f"  Installed {path.name} → {path}")
    typer.echo(f"Done! {len(installed)} binaries installed.")
