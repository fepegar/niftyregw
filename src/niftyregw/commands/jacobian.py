"""CLI command for reg_jacobian."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

_help_callback = make_help_callback("reg_jacobian")
_version_callback = make_version_callback("reg_jacobian")


def jacobian(
    transformation: Annotated[
        Path,
        typer.Option("--transformation", "-t", help="Transformation file (mandatory)."),
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    jacobian_determinant: Annotated[
        Optional[Path], typer.Option(help="Output Jacobian determinant map.")
    ] = None,
    jacobian_matrix: Annotated[
        Optional[Path], typer.Option(help="Output Jacobian matrix map (5D nifti).")
    ] = None,
    jacobian_log_determinant: Annotated[
        Optional[Path], typer.Option(help="Output log of Jacobian determinant map.")
    ] = None,
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
            help="Print the original reg_jacobian help and exit.",
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
    """Compute Jacobian-based maps from a transformation."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_jacobian")

    args: list[str] = ["-trans", str(transformation)]
    if reference is not None:
        args.extend(["-ref", str(reference)])
    if jacobian_determinant is not None:
        args.extend(["-jac", str(jacobian_determinant)])
    if jacobian_matrix is not None:
        args.extend(["-jacM", str(jacobian_matrix)])
    if jacobian_log_determinant is not None:
        args.extend(["-jacL", str(jacobian_log_determinant)])
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])

    run("reg_jacobian", *args, tool_logger=tool_logger)
