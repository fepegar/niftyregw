"""CLI command for reg_f3d."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import run

_help_callback = make_help_callback("reg_f3d")
_version_callback = make_version_callback("reg_f3d")


def f3d(
    reference: Annotated[
        Path, typer.Option("--reference", "-r", help="Reference image filename.")
    ],
    floating: Annotated[
        Path, typer.Option("--floating", "-f", help="Floating image filename.")
    ],
    # Initial transformation (one of)
    input_affine: Annotated[
        Optional[Path],
        typer.Option(
            "--input-affine",
            "-a",
            help="Input affine transformation (Affine*Reference=Floating).",
        ),
    ] = None,
    input_cpp: Annotated[
        Optional[Path],
        typer.Option(help="Input control point grid (defines coarse spacing)."),
    ] = None,
    # Output
    output_cpp: Annotated[
        Optional[Path], typer.Option(help="Output control point grid. [outputCPP.nii]")
    ] = None,
    output_result: Annotated[
        Optional[Path],
        typer.Option(
            "--output-result", "-o", help="Resampled image. [outputResult.nii]"
        ),
    ] = None,
    # Input image options
    reference_mask: Annotated[
        Optional[Path],
        typer.Option(
            "--reference-mask", "-m", help="Mask image in the reference space."
        ),
    ] = None,
    smooth_reference: Annotated[
        Optional[float], typer.Option(help="Smooth reference image (sigma in mm). [0]")
    ] = None,
    smooth_floating: Annotated[
        Optional[float], typer.Option(help="Smooth floating image (sigma in mm). [0]")
    ] = None,
    reference_lower_threshold: Annotated[
        Optional[float],
        typer.Option(help="Lower threshold for reference image intensities."),
    ] = None,
    reference_upper_threshold: Annotated[
        Optional[float],
        typer.Option(help="Upper threshold for reference image intensities."),
    ] = None,
    floating_lower_threshold: Annotated[
        Optional[float],
        typer.Option(help="Lower threshold for floating image intensities."),
    ] = None,
    floating_upper_threshold: Annotated[
        Optional[float],
        typer.Option(help="Upper threshold for floating image intensities."),
    ] = None,
    # Spline options
    spacing_x: Annotated[
        Optional[float],
        typer.Option(
            help="Final grid spacing along x in mm (voxels if negative). [5 vox]"
        ),
    ] = None,
    spacing_y: Annotated[
        Optional[float],
        typer.Option(
            help="Final grid spacing along y in mm (voxels if negative). [sx]"
        ),
    ] = None,
    spacing_z: Annotated[
        Optional[float],
        typer.Option(
            help="Final grid spacing along z in mm (voxels if negative). [sx]"
        ),
    ] = None,
    # Regularisation
    bending_energy: Annotated[
        Optional[float], typer.Option(help="Bending energy penalty weight. [0.001]")
    ] = None,
    linear_energy: Annotated[
        Optional[float],
        typer.Option(help="Linear energy (first order) penalty weight. [0.01]"),
    ] = None,
    jacobian_log_weight: Annotated[
        Optional[float],
        typer.Option(help="Log of Jacobian determinant penalty weight. [0.0]"),
    ] = None,
    no_approx_jacobian_log: Annotated[
        bool,
        typer.Option(help="Do not approximate JL only at control point positions."),
    ] = False,
    landmarks_weight: Annotated[
        Optional[float],
        typer.Option(help="Weight for landmark distance regularisation (0-1)."),
    ] = None,
    landmarks_file: Annotated[
        Optional[Path],
        typer.Option(
            help="Landmark positions file (mm): refX refY refZ floX floY floZ per line."
        ),
    ] = None,
    # Similarity measures
    use_nmi: Annotated[
        bool, typer.Option(help="Force NMI even when other measures are specified.")
    ] = False,
    reference_bins: Annotated[
        Optional[int], typer.Option(help="NMI: number of bins for reference histogram.")
    ] = None,
    floating_bins: Annotated[
        Optional[int], typer.Option(help="NMI: number of bins for floating histogram.")
    ] = None,
    lncc_sigma: Annotated[
        Optional[float],
        typer.Option(help="Use LNCC with this Gaussian kernel std dev."),
    ] = None,
    use_ssd: Annotated[
        bool, typer.Option(help="Use SSD (images normalised to 0-1).")
    ] = False,
    use_ssd_no_norm: Annotated[
        bool, typer.Option(help="Use SSD without normalisation.")
    ] = False,
    mind_offset: Annotated[
        Optional[int], typer.Option(help="Use MIND descriptor with this offset.")
    ] = None,
    mindssc_offset: Annotated[
        Optional[int], typer.Option(help="Use MIND-SSC descriptor with this offset.")
    ] = None,
    use_kld: Annotated[
        bool, typer.Option(help="Use Kullback-Leibler divergence.")
    ] = False,
    similarity_weight_image: Annotated[
        Optional[Path], typer.Option(help="Per-voxel weight image for similarity.")
    ] = None,
    robust_range: Annotated[
        bool,
        typer.Option(help="Threshold intensities between 2nd and 98th percentile."),
    ] = False,
    # Optimisation
    max_iterations: Annotated[
        Optional[int], typer.Option(help="Max iterations at the final level. [150]")
    ] = None,
    num_levels: Annotated[
        Optional[int], typer.Option(help="Number of levels for pyramids. [3]")
    ] = None,
    num_levels_to_perform: Annotated[
        Optional[int], typer.Option(help="Number of levels to run. [ln]")
    ] = None,
    no_pyramid: Annotated[
        bool, typer.Option(help="Do not use a pyramidal approach.")
    ] = False,
    no_conjugate_gradient: Annotated[
        bool,
        typer.Option(help="Use simple gradient ascent instead of conjugate gradient."),
    ] = False,
    perturbation_steps: Annotated[
        Optional[int],
        typer.Option(help="Add perturbation step(s) after each optimisation."),
    ] = None,
    # F3D2 options
    velocity_field: Annotated[
        bool, typer.Option(help="Use velocity field integration for deformation.")
    ] = False,
    no_gradient_accumulation: Annotated[
        bool, typer.Option(help="Disable gradient accumulation through exponentiation.")
    ] = False,
    floating_mask: Annotated[
        Optional[Path], typer.Option(help="Mask image in the floating space.")
    ] = None,
    # Other
    smooth_gradient: Annotated[
        Optional[float], typer.Option(help="Smooth the metric derivative (in mm). [0]")
    ] = None,
    padding: Annotated[
        Optional[float], typer.Option(help="Padding value. [nan]")
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
            help="Print the original reg_f3d help and exit.",
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
    """Fast Free-Form Deformation (F3D) non-rigid registration."""
    setup_logger(log_level)
    tool_logger = logger.bind(executable="reg_f3d")

    if (landmarks_weight is not None) != (landmarks_file is not None):
        typer.echo(
            "Both --landmarks-weight and --landmarks-file must be provided together.",
            err=True,
        )
        raise typer.Exit(code=1)

    # Check if the default output file exists before registration
    default_output = Path("outputCPP.nii")
    existed_before = default_output.exists()

    # Determine if user requested the default output path
    user_requested_default = False
    if output_cpp is not None:
        try:
            # Resolve both paths to absolute paths for comparison
            user_path = Path(output_cpp).resolve()
            default_path = default_output.resolve()
            user_requested_default = user_path == default_path
        except (OSError, RuntimeError):
            # If path resolution fails, treat as different paths
            pass

    args: list[str] = ["-ref", str(reference), "-flo", str(floating)]
    # Initial transformation
    if input_affine is not None:
        args.extend(["-aff", str(input_affine)])
    if input_cpp is not None:
        args.extend(["-incpp", str(input_cpp)])
    # Output
    if output_cpp is not None:
        args.extend(["-cpp", str(output_cpp)])
    if output_result is not None:
        args.extend(["-res", str(output_result)])
    # Input image options
    if reference_mask is not None:
        args.extend(["-rmask", str(reference_mask)])
    if smooth_reference is not None:
        args.extend(["-smooR", str(smooth_reference)])
    if smooth_floating is not None:
        args.extend(["-smooF", str(smooth_floating)])
    if reference_lower_threshold is not None:
        args.extend(["--rLwTh", str(reference_lower_threshold)])
    if reference_upper_threshold is not None:
        args.extend(["--rUpTh", str(reference_upper_threshold)])
    if floating_lower_threshold is not None:
        args.extend(["--fLwTh", str(floating_lower_threshold)])
    if floating_upper_threshold is not None:
        args.extend(["--fUpTh", str(floating_upper_threshold)])
    # Spline
    if spacing_x is not None:
        args.extend(["-sx", str(spacing_x)])
    if spacing_y is not None:
        args.extend(["-sy", str(spacing_y)])
    if spacing_z is not None:
        args.extend(["-sz", str(spacing_z)])
    # Regularisation
    if bending_energy is not None:
        args.extend(["-be", str(bending_energy)])
    if linear_energy is not None:
        args.extend(["-le", str(linear_energy)])
    if jacobian_log_weight is not None:
        args.extend(["-jl", str(jacobian_log_weight)])
    if no_approx_jacobian_log:
        args.append("-noAppJL")
    if landmarks_weight is not None and landmarks_file is not None:
        args.extend(["-land", str(landmarks_weight), str(landmarks_file)])
    # Similarity
    if use_nmi:
        args.append("--nmi")
    if reference_bins is not None:
        args.extend(["--rbn", str(reference_bins)])
    if floating_bins is not None:
        args.extend(["--fbn", str(floating_bins)])
    if lncc_sigma is not None:
        args.extend(["--lncc", str(lncc_sigma)])
    if use_ssd:
        args.append("--ssd")
    if use_ssd_no_norm:
        args.append("--ssdn")
    if mind_offset is not None:
        args.extend(["--mind", str(mind_offset)])
    if mindssc_offset is not None:
        args.extend(["--mindssc", str(mindssc_offset)])
    if use_kld:
        args.append("--kld")
    if similarity_weight_image is not None:
        args.extend(["-wSim", str(similarity_weight_image)])
    if robust_range:
        args.append("-rr")
    # Optimisation
    if max_iterations is not None:
        args.extend(["-maxit", str(max_iterations)])
    if num_levels is not None:
        args.extend(["-ln", str(num_levels)])
    if num_levels_to_perform is not None:
        args.extend(["-lp", str(num_levels_to_perform)])
    if no_pyramid:
        args.append("-nopy")
    if no_conjugate_gradient:
        args.append("-noConj")
    if perturbation_steps is not None:
        args.extend(["-pert", str(perturbation_steps)])
    # F3D2
    if velocity_field:
        args.append("-vel")
    if no_gradient_accumulation:
        args.append("-nogce")
    if floating_mask is not None:
        args.extend(["-fmask", str(floating_mask)])
    # Other
    if smooth_gradient is not None:
        args.extend(["-smoothGrad", str(smooth_gradient)])
    if padding is not None:
        args.extend(["-pad", str(padding)])
    if verbose_off:
        args.append("-voff")
    if omp_threads is not None:
        args.extend(["-omp", str(omp_threads)])

    run("reg_f3d", *args, tool_logger=tool_logger)

    # Clean up the default output file if it was created and not requested
    if not existed_before and default_output.exists() and not user_requested_default:
        try:
            default_output.unlink()
            logger.bind(executable="niftyregw").debug(
                f"Cleaned up default output file: {default_output}"
            )
        except OSError as e:
            logger.bind(executable="niftyregw").warning(
                f"Failed to clean up {default_output}: {e}"
            )
