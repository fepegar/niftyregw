"""CLI command for reg_aladin."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from niftyregw.commands import make_help_callback, make_version_callback, setup_logger
from niftyregw.enums import LogLevel
from niftyregw.wrapper import reg_aladin as _reg_aladin

_help_callback = make_help_callback("reg_aladin")
_version_callback = make_version_callback("reg_aladin")


def aladin(
    reference: Annotated[
        Path,
        typer.Option(
            "--reference",
            "-r",
            help="Reference image filename (also called Target or Fixed).",
        ),
    ],
    floating: Annotated[
        Path,
        typer.Option(
            "--floating",
            "-f",
            help="Floating image filename (also called Source or Moving).",
        ),
    ],
    # Output options
    output_affine: Annotated[
        Optional[Path],
        typer.Option(
            "--output-affine",
            "-a",
            help="Output affine transformation filename. [outputAffine.txt]",
        ),
    ] = None,
    output_result: Annotated[
        Optional[Path],
        typer.Option(
            "--output-result",
            "-o",
            help="Resampled image filename. [outputResult.nii.gz]",
        ),
    ] = None,
    # Input options
    input_affine: Annotated[
        Optional[Path],
        typer.Option(
            help="Input affine transformation filename. (Affine*Reference=Floating)",
        ),
    ] = None,
    reference_mask: Annotated[
        Optional[Path],
        typer.Option(
            help="Mask image in the reference space.",
        ),
    ] = None,
    floating_mask: Annotated[
        Optional[Path],
        typer.Option(
            help="Mask image in the floating space. (Only used when symmetric turned on)"
        ),
    ] = None,
    # Algorithm options
    no_symmetric: Annotated[
        bool, typer.Option(help="Disable the symmetric version of the algorithm.")
    ] = False,
    rigid_only: Annotated[
        bool,
        typer.Option(
            help="Perform a rigid registration only. (Rigid+affine by default)"
        ),
    ] = False,
    affine_direct: Annotated[
        bool, typer.Option(help="Directly optimize 12 DoF affine.")
    ] = False,
    max_iterations: Annotated[
        Optional[int],
        typer.Option(
            help="Max iterations of the trimmed least square approach per level. [5]"
        ),
    ] = None,
    num_levels: Annotated[
        Optional[int],
        typer.Option(help="Number of levels for the coarse-to-fine pyramids. [3]"),
    ] = None,
    num_levels_to_perform: Annotated[
        Optional[int],
        typer.Option(help="Number of levels to run the registration. [ln]"),
    ] = None,
    smooth_reference: Annotated[
        Optional[float],
        typer.Option(
            help="Gaussian smoothing std dev (mm) for the reference image. [0]"
        ),
    ] = None,
    smooth_floating: Annotated[
        Optional[float],
        typer.Option(
            help="Gaussian smoothing std dev (mm) for the floating image. [0]"
        ),
    ] = None,
    reference_lower_threshold: Annotated[
        Optional[float],
        typer.Option(help="Lower threshold for the reference image. [0]"),
    ] = None,
    reference_upper_threshold: Annotated[
        Optional[float],
        typer.Option(help="Upper threshold for the reference image. [0]"),
    ] = None,
    floating_lower_threshold: Annotated[
        Optional[float],
        typer.Option(help="Lower threshold for the floating image. [0]"),
    ] = None,
    floating_upper_threshold: Annotated[
        Optional[float],
        typer.Option(help="Upper threshold for the floating image. [0]"),
    ] = None,
    padding: Annotated[
        Optional[float], typer.Option(help="Padding value. [nan]")
    ] = None,
    # Initialisation options
    use_nifti_origin: Annotated[
        bool,
        typer.Option(
            help="Use the nifti header origin to initialise the transformation."
        ),
    ] = False,
    use_masks_centre_of_mass: Annotated[
        bool,
        typer.Option(
            help="Use the input masks centre of mass to initialise the transformation."
        ),
    ] = False,
    use_images_centre_of_mass: Annotated[
        bool,
        typer.Option(
            help="Use the input images centre of mass to initialise the transformation."
        ),
    ] = False,
    # Other options
    interpolation: Annotated[
        Optional[int],
        typer.Option(help="Interpolation order to warp the floating image."),
    ] = None,
    isotropic: Annotated[
        bool,
        typer.Option(help="Make floating and reference images isotropic if required."),
    ] = False,
    percent_blocks_to_use: Annotated[
        Optional[int],
        typer.Option(
            help="Percentage of blocks to use in the optimisation scheme. [50]"
        ),
    ] = None,
    percent_inliers: Annotated[
        Optional[int],
        typer.Option(help="Percentage of blocks to consider as inlier. [50]"),
    ] = None,
    block_step_size_2: Annotated[
        bool,
        typer.Option(
            help="Use a block step size of 2 (instead of 1) for faster, less accurate registration."
        ),
    ] = False,
    omp_threads: Annotated[
        Optional[int], typer.Option(help="Number of threads to use with OpenMP.")
    ] = None,
    verbose_off: Annotated[bool, typer.Option(help="Turn verbose off.")] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            is_eager=True,
            callback=_version_callback,
            help="Print reg_aladin version and exit.",
        ),
    ] = False,
    _: Annotated[
        bool,
        typer.Option(
            "--print-help",
            "-h",
            is_eager=True,
            callback=_help_callback,
            help="Print the original reg_aladin help and exit.",
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
    """Block-matching global (affine/rigid) registration."""
    setup_logger(log_level)

    _reg_aladin(
        reference,
        floating,
        output_affine=output_affine,
        output_result=output_result,
        input_affine=input_affine,
        reference_mask=reference_mask,
        floating_mask=floating_mask,
        no_symmetric=no_symmetric,
        rigid_only=rigid_only,
        affine_direct=affine_direct,
        max_iterations=max_iterations,
        num_levels=num_levels,
        num_levels_to_perform=num_levels_to_perform,
        smooth_reference=smooth_reference,
        smooth_floating=smooth_floating,
        reference_lower_threshold=reference_lower_threshold,
        reference_upper_threshold=reference_upper_threshold,
        floating_lower_threshold=floating_lower_threshold,
        floating_upper_threshold=floating_upper_threshold,
        padding=padding,
        use_nifti_origin=use_nifti_origin,
        use_masks_centre_of_mass=use_masks_centre_of_mass,
        use_images_centre_of_mass=use_images_centre_of_mass,
        interpolation=interpolation,
        isotropic=isotropic,
        percent_blocks_to_use=percent_blocks_to_use,
        percent_inliers=percent_inliers,
        block_step_size_2=block_step_size_2,
        omp_threads=omp_threads,
        verbose_off=verbose_off,
    )
