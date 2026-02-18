"""Python wrapper for NiftyReg binaries."""

from __future__ import annotations

from pathlib import Path
from subprocess import PIPE, Popen

import loguru
from loguru import logger

from .install import find as _find


def _get_path(tool: str) -> Path:
    path = _find(tool)
    if path is None:
        msg = f"{tool} not found. Please install NiftyReg first."
        raise FileNotFoundError(msg)
    return path


def run(tool: str, *args: str, tool_logger: loguru.Logger | None = None) -> None:
    """Run any NiftyReg binary with raw CLI arguments.

    Args:
        tool: Binary name (e.g. ``"reg_aladin"``).
        *args: Raw CLI arguments.
        tool_logger: Optional loguru logger for structured output.
    """
    tool_path = _get_path(tool)
    args_list = [arg.strip("\\\n") for arg in args]
    args_list = [arg for arg in args_list if arg]

    cmd = [str(tool_path), *args_list]
    with Popen(cmd, stdout=PIPE, stderr=PIPE, text=True, bufsize=1) as p:
        assert p.stdout is not None
        assert p.stderr is not None

        for line in p.stderr:
            line = line.rstrip("\n")
            if tool_logger is None:
                print(line)
                continue
            if line.startswith("[NiftyReg WARNING]"):
                log = tool_logger.warning
            elif line.startswith("[NiftyReg ERROR]"):
                log = tool_logger.error
            else:
                log = tool_logger.info
            log(line)

        for line in p.stdout:
            line = line.rstrip("\n")
            if tool_logger is None:
                print(line)
            else:
                tool_logger.info(line)


def reg_aladin(
    reference: Path,
    floating: Path,
    *,
    output_affine: Path | None = None,
    output_result: Path | None = None,
    input_affine: Path | None = None,
    reference_mask: Path | None = None,
    floating_mask: Path | None = None,
    no_symmetric: bool = False,
    rigid_only: bool = False,
    affine_direct: bool = False,
    max_iterations: int | None = None,
    num_levels: int | None = None,
    num_levels_to_perform: int | None = None,
    smooth_reference: float | None = None,
    smooth_floating: float | None = None,
    reference_lower_threshold: float | None = None,
    reference_upper_threshold: float | None = None,
    floating_lower_threshold: float | None = None,
    floating_upper_threshold: float | None = None,
    padding: float | None = None,
    use_nifti_origin: bool = False,
    use_masks_centre_of_mass: bool = False,
    use_images_centre_of_mass: bool = False,
    interpolation: int | None = None,
    isotropic: bool = False,
    percent_blocks_to_use: int | None = None,
    percent_inliers: int | None = None,
    block_step_size_2: bool = False,
    omp_threads: int | None = None,
    verbose_off: bool = False,
) -> None:
    """Run reg_aladin with structured arguments.

    Args:
        reference: Reference image path (also called Target or Fixed).
        floating: Floating image path (also called Source or Moving).
        output_affine: Output affine transformation filename.
        output_result: Resampled image filename.
        input_affine: Input affine transformation filename.
        reference_mask: Mask image in the reference space.
        floating_mask: Mask image in the floating space.
        no_symmetric: Disable the symmetric version of the algorithm.
        rigid_only: Perform a rigid registration only.
        affine_direct: Directly optimize 12 DoF affine.
        max_iterations: Max iterations per level.
        num_levels: Number of levels for pyramids.
        num_levels_to_perform: Number of levels to run.
        smooth_reference: Gaussian smoothing std dev (mm) for reference.
        smooth_floating: Gaussian smoothing std dev (mm) for floating.
        reference_lower_threshold: Lower threshold for reference image.
        reference_upper_threshold: Upper threshold for reference image.
        floating_lower_threshold: Lower threshold for floating image.
        floating_upper_threshold: Upper threshold for floating image.
        padding: Padding value.
        use_nifti_origin: Use nifti header origin for initialisation.
        use_masks_centre_of_mass: Use masks centre of mass for initialisation.
        use_images_centre_of_mass: Use images centre of mass for initialisation.
        interpolation: Interpolation order.
        isotropic: Make images isotropic if required.
        percent_blocks_to_use: Percentage of blocks in optimisation.
        percent_inliers: Percentage of inlier blocks.
        block_step_size_2: Use block step size of 2 for faster registration.
        omp_threads: Number of OpenMP threads.
        verbose_off: Turn verbose off.
    """
    command_lines: list[str] = [
        f"  -ref {reference} \\",
        f"  -flo {floating} \\",
    ]

    if output_affine is not None:
        command_lines.append(f"  -aff {output_affine} \\")
    if output_result is not None:
        command_lines.append(f"  -res {output_result} \\")
    if input_affine is not None:
        command_lines.append(f"  -inaff {input_affine} \\")
    if reference_mask is not None:
        command_lines.append(f"  -rmask {reference_mask} \\")
    if floating_mask is not None:
        command_lines.append(f"  -fmask {floating_mask} \\")
    if no_symmetric:
        command_lines.append("  -noSym \\")
    if rigid_only:
        command_lines.append("  -rigOnly \\")
    if affine_direct:
        command_lines.append("  -affDirect \\")
    if max_iterations is not None:
        command_lines.append(f"  -maxit {max_iterations} \\")
    if num_levels is not None:
        command_lines.append(f"  -ln {num_levels} \\")
    if num_levels_to_perform is not None:
        command_lines.append(f"  -lp {num_levels_to_perform} \\")
    if smooth_reference is not None:
        command_lines.append(f"  -smooR {smooth_reference} \\")
    if smooth_floating is not None:
        command_lines.append(f"  -smooF {smooth_floating} \\")
    if reference_lower_threshold is not None:
        command_lines.append(f"  -refLowThr {reference_lower_threshold} \\")
    if reference_upper_threshold is not None:
        command_lines.append(f"  -refUpThr {reference_upper_threshold} \\")
    if floating_lower_threshold is not None:
        command_lines.append(f"  -floLowThr {floating_lower_threshold} \\")
    if floating_upper_threshold is not None:
        command_lines.append(f"  -floUpThr {floating_upper_threshold} \\")
    if padding is not None:
        command_lines.append(f"  -pad {padding} \\")
    if use_nifti_origin:
        command_lines.append("  -nac \\")
    if use_masks_centre_of_mass:
        command_lines.append("  -comm \\")
    if use_images_centre_of_mass:
        command_lines.append("  -comi \\")
    if interpolation is not None:
        command_lines.append(f"  -interp {interpolation} \\")
    if isotropic:
        command_lines.append("  -iso \\")
    if percent_blocks_to_use is not None:
        command_lines.append(f"  -pv {percent_blocks_to_use} \\")
    if percent_inliers is not None:
        command_lines.append(f"  -pi {percent_inliers} \\")
    if block_step_size_2:
        command_lines.append("  -speeeeed \\")
    if omp_threads is not None:
        command_lines.append(f"  -omp {omp_threads} \\")
    if verbose_off:
        command_lines.append("  -voff \\")

    _run_with_logging("reg_aladin", *command_lines)


def _run_with_logging(tool: str, *lines: str) -> None:
    tool_path = _get_path(tool)
    loggerw = logger.bind(executable="niftyregw")
    loggerx = logger.bind(executable=tool)

    loggerw.debug("The following command will be run:")
    lines_str = "\n".join(lines).strip(" \\")
    loggerw.debug(f"{tool_path} \\\n  {lines_str}")
    args = []
    for line in lines:
        args.extend(line.strip(" \\").split())

    run(tool, *args, tool_logger=loggerx)


def reg_aladin_raw(*args: str, logger: loguru.Logger | None = None) -> None:
    """Run reg_aladin with raw CLI arguments.

    Args:
        *args: Raw CLI arguments to pass to reg_aladin.
        logger: Optional loguru logger for structured output.
    """
    run("reg_aladin", *args, tool_logger=logger)
