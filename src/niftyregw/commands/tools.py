"""CLI command for reg_tools."""

from pathlib import Path
from typing import Annotated, Optional, Tuple

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

_help_callback = make_help_callback("reg_tools")
_version_callback = make_version_callback("reg_tools")


def tools(
    input_image: Annotated[
        Path, typer.Option("--input", "-i", help="Input image filename.")
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output image filename. [output.nii]"),
    ] = None,
    # Type conversion
    to_float: Annotated[
        bool, typer.Option(help="Convert the input image to float.")
    ] = False,
    # Geometric
    downsample: Annotated[
        bool, typer.Option(help="Downsample the input image 2 times.")
    ] = False,
    isotropic: Annotated[
        bool, typer.Option(help="Make the resulting image isotropic.")
    ] = False,
    change_resolution: Annotated[
        Optional[Tuple[float, float, float]],
        typer.Option(help="Resample to specified resolution in mm (x y z)."),
    ] = None,
    # Smoothing
    smooth_spline: Annotated[
        Optional[Tuple[float, float, float]],
        typer.Option(help="Smooth with cubic b-spline kernel (sx sy sz)."),
    ] = None,
    smooth_gaussian: Annotated[
        Optional[Tuple[float, float, float]],
        typer.Option(help="Smooth with Gaussian kernel (sx sy sz)."),
    ] = None,
    smooth_labels: Annotated[
        Optional[Tuple[float, float, float]],
        typer.Option(help="Smooth label image with Gaussian kernel (sx sy sz)."),
    ] = None,
    # Arithmetic
    add: Annotated[
        Optional[str], typer.Option(help="Add an image or value to the input.")
    ] = None,
    subtract: Annotated[
        Optional[str], typer.Option(help="Subtract an image or value from the input.")
    ] = None,
    multiply: Annotated[
        Optional[str], typer.Option(help="Multiply the input by an image or value.")
    ] = None,
    divide: Annotated[
        Optional[str], typer.Option(help="Divide the input by an image or value.")
    ] = None,
    # Thresholding and masking
    binarize: Annotated[
        bool, typer.Option(help="Binarise the input image (val!=0 -> 1).")
    ] = False,
    threshold: Annotated[
        Optional[float],
        typer.Option(help="Threshold the input image (val<thr -> 0, else 1)."),
    ] = None,
    nan_mask: Annotated[
        Optional[Path], typer.Option(help="Mask image; voxels outside are set to NaN.")
    ] = None,
    rms: Annotated[
        Optional[Path],
        typer.Option(help="Compute mean RMS between input and this image."),
    ] = None,
    remove_nan_inf: Annotated[
        Optional[float], typer.Option(help="Replace NaN and Inf with this value.")
    ] = None,
    # Header
    no_scaling: Annotated[
        bool, typer.Option(help="Set scl_slope=1 and scl_inter=0.")
    ] = False,
    # Format conversion
    to_rgb: Annotated[
        bool, typer.Option("--to-rgb", help="Convert 4D/5D to RGB nifti.")
    ] = False,
    # Descriptors
    mind: Annotated[bool, typer.Option(help="Create a MIND descriptor image.")] = False,
    mindssc: Annotated[
        bool, typer.Option(help="Create a MIND-SSC descriptor image.")
    ] = False,
    test_active_blocks: Annotated[
        bool,
        typer.Option(help="Highlight active blocks for reg_aladin (block variance)."),
    ] = False,
    # Other
    interpolation: Annotated[
        Optional[int], typer.Option(help="Interpolation order to warp the image.")
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
            help="Print the original reg_tools help and exit.",
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
    """Image manipulation tools."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_tools")

    args: list[str] = ["-in", str(input_image)]
    if output is not None:
        args.extend(["-out", str(output)])
    if to_float:
        args.append("-float")
    if downsample:
        args.append("-down")
    if isotropic:
        args.append("-iso")
    if change_resolution is not None:
        args.extend(
            [
                "-chgres",
                str(change_resolution[0]),
                str(change_resolution[1]),
                str(change_resolution[2]),
            ]
        )
    if smooth_spline is not None:
        args.extend(
            [
                "-smoS",
                str(smooth_spline[0]),
                str(smooth_spline[1]),
                str(smooth_spline[2]),
            ]
        )
    if smooth_gaussian is not None:
        args.extend(
            [
                "-smoG",
                str(smooth_gaussian[0]),
                str(smooth_gaussian[1]),
                str(smooth_gaussian[2]),
            ]
        )
    if smooth_labels is not None:
        args.extend(
            [
                "-smoL",
                str(smooth_labels[0]),
                str(smooth_labels[1]),
                str(smooth_labels[2]),
            ]
        )
    if add is not None:
        args.extend(["-add", add])
    if subtract is not None:
        args.extend(["-sub", subtract])
    if multiply is not None:
        args.extend(["-mul", multiply])
    if divide is not None:
        args.extend(["-div", divide])
    if binarize:
        args.append("-bin")
    if threshold is not None:
        args.extend(["-thr", str(threshold)])
    if nan_mask is not None:
        args.extend(["-nan", str(nan_mask)])
    if rms is not None:
        args.extend(["-rms", str(rms)])
    if remove_nan_inf is not None:
        args.extend(["-rmNanInf", str(remove_nan_inf)])
    if no_scaling:
        args.append("-noscl")
    if to_rgb:
        args.append("-4d2rgb")
    if mind:
        args.append("-mind")
    if mindssc:
        args.append("-mindssc")
    if test_active_blocks:
        args.append("-testActiveBlocks")
    if interpolation is not None:
        args.extend(["-interp", str(interpolation)])
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])

    run("reg_tools", *args, tool_logger=tool_logger)
