"""CLI command for reg_transform."""

from pathlib import Path
from typing import Annotated, Optional, Tuple

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Manipulate and compose transformations.",
)

_help_callback = make_help_callback("reg_transform")


@app.callback()
def _main(
    _: Annotated[
        bool,
        typer.Option(
            "--print-help",
            "-h",
            is_eager=True,
            callback=_help_callback,
            help="Print the original reg_transform help and exit.",
        ),
    ] = False,
) -> None:
    pass


# ---------------------------------------------------------------------------
# Shared option patterns
# ---------------------------------------------------------------------------


def _run_transform(
    args: list[str], log_level: LogLevel, omp_threads: Optional[int] = None
) -> None:
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_transform")
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])
    run("reg_transform", *args, tool_logger=tool_logger)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------


@app.command("deformation")
def deformation(
    input_transformation: Annotated[
        Path, typer.Option("--input", "-i", help="Input transformation file.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output deformation field file.")
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Compute a deformation field from a transformation."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-def", str(input_transformation), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("displacement")
def displacement(
    input_transformation: Annotated[
        Path, typer.Option("--input", "-i", help="Input transformation file.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output displacement field file.")
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Compute a displacement field from a transformation."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-disp", str(input_transformation), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("flow")
def flow(
    input_transformation: Annotated[
        Path, typer.Option("--input", "-i", help="Input spline parametrised SVF.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output flow field file.")
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Compute a flow field from a spline parametrised SVF."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-flow", str(input_transformation), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("compose")
def compose(
    input1: Annotated[
        Path, typer.Option("--input1", "-i", help="First transformation file.")
    ],
    input2: Annotated[
        Path, typer.Option("--input2", "-j", help="Second transformation file.")
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o", help="Output deformation field: T3(x) = T2(T1(x))."
        ),
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference", "-r", help="Reference image for input1 (if spline)."
        ),
    ] = None,
    reference2: Annotated[
        Optional[Path], typer.Option(help="Reference image for input2 (if spline).")
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Compose two transformations into a deformation field."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    if reference2 is not None:
        args.extend(["-ref2", str(reference2)])
    args.extend(["-comp", str(input1), str(input2), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("landmarks")
def landmarks(
    transformation: Annotated[
        Path, typer.Option("--transformation", "-t", help="Transformation file.")
    ],
    input_landmarks: Annotated[
        Path, typer.Option("--input", "-i", help="Input landmark file (mm positions).")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output landmark file.")
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Apply a transformation to a set of landmarks."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-land", str(transformation), str(input_landmarks), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("update-sform")
def update_sform(
    input_image: Annotated[
        Path, typer.Option("--input", "-i", help="Image to be updated.")
    ],
    affine: Annotated[
        Path,
        typer.Option(
            "--affine", "-a", help="Affine transformation (Affine*Reference=Floating)."
        ),
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output updated image.")
    ],
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Update the sform of an image using an affine transformation."""
    args: list[str] = ["-updSform", str(input_image), str(affine), str(output)]
    _run_transform(args, log_level, omp_threads)


@app.command("invert-affine")
def invert_affine(
    input_affine: Annotated[
        Path, typer.Option("--input", "-i", help="Input affine transformation file.")
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o", help="Output inverted affine transformation file."
        ),
    ],
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Invert an affine matrix."""
    args: list[str] = ["-invAff", str(input_affine), str(output)]
    _run_transform(args, log_level, omp_threads)


@app.command("invert-nonrigid")
def invert_nonrigid(
    input_transformation: Annotated[
        Path, typer.Option("--input", "-i", help="Input transformation file.")
    ],
    floating: Annotated[
        Path,
        typer.Option(
            "--floating",
            "-f",
            help="Floating image where inverted transformation is defined.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output inverted transformation file."),
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Invert a non-rigid transformation (saved as deformation field)."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-invNrr", str(input_transformation), str(floating), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("half")
def half(
    input_transformation: Annotated[
        Path, typer.Option("--input", "-i", help="Input transformation file.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output halved transformation file.")
    ],
    reference: Annotated[
        Optional[Path],
        typer.Option(
            "--reference",
            "-r",
            help="Reference image (required for spline parametrisation).",
        ),
    ] = None,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Halve a transformation (same type preserved)."""
    args: list[str] = []
    if reference is not None:
        args.extend(["-ref", str(reference)])
    args.extend(["-half", str(input_transformation), str(output)])
    _run_transform(args, log_level, omp_threads)


@app.command("make-affine")
def make_affine(
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output affine transformation file.")
    ],
    rotation: Annotated[
        Tuple[float, float, float], typer.Option(help="Rotation angles (rx ry rz).")
    ],
    translation: Annotated[
        Tuple[float, float, float], typer.Option(help="Translation (tx ty tz).")
    ],
    scaling: Annotated[
        Tuple[float, float, float], typer.Option(help="Scaling factors (sx sy sz).")
    ],
    shearing: Annotated[
        Tuple[float, float, float], typer.Option(help="Shearing (shx shy shz).")
    ],
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Create an affine transformation matrix from parameters."""
    params = [
        str(rotation[0]),
        str(rotation[1]),
        str(rotation[2]),
        str(translation[0]),
        str(translation[1]),
        str(translation[2]),
        str(scaling[0]),
        str(scaling[1]),
        str(scaling[2]),
        str(shearing[0]),
        str(shearing[1]),
        str(shearing[2]),
    ]
    args: list[str] = ["-makeAff", *params, str(output)]
    _run_transform(args, log_level, omp_threads)


@app.command("affine-to-rigid")
def affine_to_rigid(
    input_affine: Annotated[
        Path, typer.Option("--input", "-i", help="Input affine transformation file.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output rigid transformation file.")
    ],
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Extract the rigid component from an affine transformation."""
    args: list[str] = ["-aff2rig", str(input_affine), str(output)]
    _run_transform(args, log_level, omp_threads)


@app.command("flirt-to-niftyreg")
def flirt_to_niftyreg(
    input_flirt: Annotated[
        Path,
        typer.Option("--input", "-i", help="Input FLIRT (FSL) affine transformation."),
    ],
    reference: Annotated[
        Path,
        typer.Option("--reference", "-r", help="Reference image used in FLIRT (-ref)."),
    ],
    floating: Annotated[
        Path,
        typer.Option("--floating", "-f", help="Floating image used in FLIRT (-in)."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output NiftyReg affine transformation."),
    ],
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of OpenMP threads.")
    ] = None,
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
    """Convert a FLIRT (FSL) affine to a NiftyReg affine."""
    args: list[str] = [
        "-flirtAff2NR",
        str(input_flirt),
        str(reference),
        str(floating),
        str(output),
    ]
    _run_transform(args, log_level, omp_threads)
