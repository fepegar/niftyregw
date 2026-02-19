"""CLI command for reg_resample."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

_help_callback = make_help_callback("reg_resample")
_version_callback = make_version_callback("reg_resample")


def resample(
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image filename.")
    ],
    floating: Annotated[
        Path, typer.Option("--floating", "-f", help="Floating image filename.")
    ],
    transformation: Annotated[
        Optional[Path],
        typer.Option(
            "--transformation",
            "-t",
            help="Transformation file (from reg_aladin, reg_f3d, or reg_transform).",
        ),
    ] = None,
    output_result: Annotated[
        Optional[Path],
        typer.Option("--output-result", "-o", help="Resampled image filename."),
    ] = None,
    output_blank: Annotated[
        Optional[Path], typer.Option(help="Resampled blank grid filename.")
    ] = None,
    interpolation: Annotated[
        Optional[int],
        typer.Option(help="Interpolation order (0=NN, 1=LIN, 3=CUB, 4=SINC). [3]"),
    ] = None,
    padding: Annotated[
        Optional[float], typer.Option(help="Interpolation padding value. [0]")
    ] = None,
    tensor: Annotated[
        bool,
        typer.Option(
            help="Treat last 6 timepoints as tensor (XX, XY, YY, XZ, YZ, ZZ)."
        ),
    ] = False,
    psf: Annotated[
        bool, typer.Option(help="Two-step resampling for lower resolution.")
    ] = False,
    psf_algorithm: Annotated[
        Optional[int],
        typer.Option(
            help="PSF algorithm: minimise matrix metric (0) or determinant (1). [0]"
        ),
    ] = None,
    verbose_off: Annotated[bool, typer.Option(help="Turn verbose off.")] = False,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of threads to use with OpenMP.")
    ] = None,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            is_eager=True,
            callback=_version_callback,
            help="Print version and exit.",
        ),
    ] = False,
    _: Annotated[
        bool,
        typer.Option(
            "--print-help",
            "-h",
            is_eager=True,
            callback=_help_callback,
            help="Print the original reg_resample help and exit.",
        ),
    ] = False,
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
    """Resample an image with a given transformation."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_resample")

    args: list[str] = ["-ref", str(reference), "-flo", str(floating)]
    if transformation is not None:
        args.extend(["-trans", str(transformation)])
    if output_result is not None:
        args.extend(["-res", str(output_result)])
    if output_blank is not None:
        args.extend(["-blank", str(output_blank)])
    if interpolation is not None:
        args.extend(["-inter", str(interpolation)])
    if padding is not None:
        args.extend(["-pad", str(padding)])
    if tensor:
        args.append("-tensor")
    if psf:
        args.append("-psf")
    if psf_algorithm is not None:
        args.extend(["-psf_alg", str(psf_algorithm)])
    if verbose_off:
        args.append("-voff")
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])

    run("reg_resample", *args, tool_logger=tool_logger)
