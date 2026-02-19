# `niftyregw`

Pythonic wrapper for [NiftyReg](https://github.com/KCL-BMEIS/niftyreg), providing
a modern CLI and Python API for medical image registration.

NiftyReg is a suite of tools for efficient medical image registration, developed
at [King's College London](https://www.kcl.ac.uk/).

## Installation

```shell
pip install niftyregw
```

Or with [`uv`](https://docs.astral.sh/uv/):

```shell
uv pip install niftyregw
```

## CLI

```shell
niftyregw --help
```

### Affine registration

```shell
niftyregw aladin \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --output-affine affine.txt \
  --output-result result.nii.gz
```

### Non-rigid registration

```shell
niftyregw f3d \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --input-affine affine.txt \
  --output-cpp cpp.nii.gz \
  --output-result result.nii.gz
```

### All subcommands

| Subcommand  | Description                                          |
|-------------|------------------------------------------------------|
| `install`   | Download and install NiftyReg binaries               |
| `aladin`    | Block-matching global (affine/rigid) registration    |
| `f3d`       | Fast Free-Form Deformation non-rigid registration    |
| `measure`   | Compute similarity measures between images           |
| `jacobian`  | Compute Jacobian-based maps from transformations     |
| `resample`  | Resample an image with a given transformation        |
| `tools`     | Image manipulation tools                             |
| `average`   | Average images or transformations                    |
| `transform` | Manipulate and compose transformations               |

## Python

```python
from niftyregw import reg_aladin

reg_aladin(
    reference="ref.nii.gz",
    floating="flo.nii.gz",
    output_affine="affine.txt",
    output_result="result.nii.gz",
    rigid_only=True,
)
```

For any binary, use the generic `run` function:

```python
from niftyregw import run

run("reg_f3d", "-ref", "ref.nii.gz", "-flo", "flo.nii.gz")
```
