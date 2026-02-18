"""CLI command for reg_average."""

from pathlib import Path
from typing import Annotated, List

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Average images or transformations.",
)

_help_callback = make_help_callback("reg_average")


@app.callback()
def _main(
    _: Annotated[
        bool,
        typer.Option(
            "--print-help",
            "-h",
            is_eager=True,
            callback=_help_callback,
            help="Print the original reg_average help and exit.",
        ),
    ] = False,
) -> None:
    pass


@app.command("avg")
def avg(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    inputs: Annotated[
        List[Path], typer.Argument(help="Input images or affine matrices to average.")
    ],
    nearest_neighbour: Annotated[
        bool, typer.Option("--nn", help="Use nearest neighbour interpolation.")
    ] = False,
    linear: Annotated[
        bool, typer.Option("--lin", help="Use linear interpolation.")
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
    """Average images or affine matrices."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    args: list[str] = [str(output), "-avg"] + [str(p) for p in inputs]
    if nearest_neighbour:
        args.append("--NN")
    if linear:
        args.append("--LIN")
    run("reg_average", *args, tool_logger=tool_logger)


@app.command("avg-lts")
def avg_lts(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    inputs: Annotated[
        List[Path],
        typer.Argument(help="Input affine matrices (half treated as outliers)."),
    ],
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
    """Robust average of affine matrices (LTS, half are outliers)."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    args: list[str] = [str(output), "-avg_lts"] + [str(p) for p in inputs]
    run("reg_average", *args, tool_logger=tool_logger)


@app.command("avg-tran")
def avg_tran(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image.")
    ],
    inputs: Annotated[
        List[Path],
        typer.Argument(
            help="Alternating transformation and floating image files: trans1 flo1 trans2 flo2 ..."
        ),
    ],
    nearest_neighbour: Annotated[
        bool, typer.Option("--nn", help="Use nearest neighbour interpolation.")
    ] = False,
    linear: Annotated[
        bool, typer.Option("--lin", help="Use linear interpolation.")
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
    """Resample all images into reference space and average (cubic spline)."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    args: list[str] = [str(output), "-avg_tran", str(reference)] + [
        str(p) for p in inputs
    ]
    if nearest_neighbour:
        args.append("--NN")
    if linear:
        args.append("--LIN")
    run("reg_average", *args, tool_logger=tool_logger)


@app.command("demean")
def demean(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image.")
    ],
    inputs: Annotated[
        List[Path],
        typer.Argument(
            help="Alternating transformation and floating image files: trans1 flo1 trans2 flo2 ..."
        ),
    ],
    nearest_neighbour: Annotated[
        bool, typer.Option("--nn", help="Use nearest neighbour interpolation.")
    ] = False,
    linear: Annotated[
        bool, typer.Option("--lin", help="Use linear interpolation.")
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
    """Demean transformations (enforce mean identity)."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    args: list[str] = [str(output), "-demean", str(reference)] + [
        str(p) for p in inputs
    ]
    if nearest_neighbour:
        args.append("--NN")
    if linear:
        args.append("--LIN")
    run("reg_average", *args, tool_logger=tool_logger)


@app.command("demean-noaff")
def demean_noaff(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image.")
    ],
    inputs: Annotated[
        List[Path],
        typer.Argument(
            help="Triples of affine, non-rigid transformation, and floating image: aff1 nr1 flo1 ..."
        ),
    ],
    nearest_neighbour: Annotated[
        bool, typer.Option("--nn", help="Use nearest neighbour interpolation.")
    ] = False,
    linear: Annotated[
        bool, typer.Option("--lin", help="Use linear interpolation.")
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
    """Demean with explicit affine removal from non-rigid transformations."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    args: list[str] = [str(output), "-demean_noaff", str(reference)] + [
        str(p) for p in inputs
    ]
    if nearest_neighbour:
        args.append("--NN")
    if linear:
        args.append("--LIN")
    run("reg_average", *args, tool_logger=tool_logger)


@app.command("cmd-file")
def cmd_file(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output filename.")],
    command_file: Annotated[
        Path,
        typer.Option(
            "--command-file", "-c", help="Text file containing the full command."
        ),
    ],
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
    """Run reg_average from a command file."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_average")
    run(
        "reg_average",
        str(output),
        "--cmd_file",
        str(command_file),
        tool_logger=tool_logger,
    )
