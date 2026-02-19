# Python API

`niftyregw` provides a typed Python API alongside its CLI.

## `reg_aladin`

The `reg_aladin` function runs affine registration with full type annotations.

```python
from niftyregw import reg_aladin

reg_aladin(
    reference="ref.nii.gz",
    floating="flo.nii.gz",
    output_affine="affine.txt",
    output_result="result.nii.gz",
    rigid_only=True,
    num_levels=4,
    max_iterations=10,
)
```

??? info "Full signature"

    ```python
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
    ) -> None: ...
    ```

## `run`

For binaries without a dedicated typed function, use `run` to call any NiftyReg
binary with raw arguments:

```python
from niftyregw import run

# Non-rigid registration
run(
    "reg_f3d",
    "-ref", "ref.nii.gz",
    "-flo", "flo.nii.gz",
    "-cpp", "cpp.nii.gz",
    "-res", "result.nii.gz",
)

# Compute Jacobian determinant
run(
    "reg_jacobian",
    "-ref", "ref.nii.gz",
    "-trans", "cpp.nii.gz",
    "-jac", "jac_det.nii.gz",
)
```

## Logging

`niftyregw` uses [Loguru](https://github.com/Delgan/loguru) for structured
logging. NiftyReg's output is classified by level:

- Lines starting with `[NiftyReg WARNING]` → `WARNING` (prefix stripped)
- Lines starting with `[NiftyReg ERROR]` → `ERROR` (prefix stripped)
- Lines starting with `[NiftyReg INFO]` → `INFO` (prefix stripped)
- All other lines → `INFO`

You can pass a custom logger to `run`:

```python
from loguru import logger
from niftyregw import run

my_logger = logger.bind(executable="reg_aladin")
run("reg_aladin", "-ref", "ref.nii.gz", "-flo", "flo.nii.gz", tool_logger=my_logger)
```
