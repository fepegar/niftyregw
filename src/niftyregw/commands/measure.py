"""CLI command for reg_measure."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

_help_callback = make_help_callback("reg_measure")
_version_callback = make_version_callback("reg_measure")


def measure(
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image filename.")
    ],
    floating: Annotated[
        Path, typer.Option("--floating", "-f", help="Floating image filename.")
    ],
    ncc: Annotated[
        bool, typer.Option(help="Compute NCC (Normalized Cross-Correlation).")
    ] = False,
    lncc: Annotated[bool, typer.Option(help="Compute LNCC (Local NCC).")] = False,
    nmi: Annotated[
        bool, typer.Option(help="Compute NMI (Normalized Mutual Information, 64 bins).")
    ] = False,
    ssd: Annotated[
        bool, typer.Option(help="Compute SSD (Sum of Squared Differences).")
    ] = False,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output text file. [stdout]"),
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
            help="Print the original reg_measure help and exit.",
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
    """Compute similarity measures between two images."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_measure")

    args: list[str] = ["-ref", str(reference), "-flo", str(floating)]
    if ncc:
        args.append("-ncc")
    if lncc:
        args.append("-lncc")
    if nmi:
        args.append("-nmi")
    if ssd:
        args.append("-ssd")
    if output is not None:
        args.extend(["-out", str(output)])
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])

    run("reg_measure", *args, tool_logger=tool_logger)
