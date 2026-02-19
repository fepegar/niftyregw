# CLI reference

`niftyregw` provides subcommands for all 8 NiftyReg binaries. Option names use
descriptive English instead of the terse NiftyReg flags.

```shell
niftyregw --help
```

!!! tip "Original help"

    Every subcommand supports `-h` to print the **original** NiftyReg help
    message, and `--help` for the `niftyregw` help.

## `install`

Download and install NiftyReg binaries for your platform.

```shell
niftyregw install
niftyregw install --output-dir /opt/niftyreg/bin
```

| Option | Short | Description |
|--------|-------|-------------|
| `--output-dir` | `-o` | Directory to install binaries into (default: `~/.local/bin`) |

## `aladin`

Block-matching global (affine/rigid) registration.

```shell
niftyregw aladin \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --output-affine affine.txt \
  --output-result result.nii.gz
```

Common options:

| Option | Short | Description |
|--------|-------|-------------|
| `--reference` | `-r` | Reference (target/fixed) image |
| `--floating` | `-f` | Floating (source/moving) image |
| `--output-result` | `-o` | Resampled output image |
| `--output-affine` | `-a` | Output affine transformation |
| `--input-affine` | `-i` | Input affine transformation |
| `--reference-mask` | `-m` | Mask in reference space |
| `--rigid-only` | | Rigid registration only |
| `--num-levels` | | Pyramid levels |
| `--max-iterations` | | Max iterations per level |

## `f3d`

Fast Free-Form Deformation (F3D) non-rigid registration.

```shell
niftyregw f3d \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --input-affine affine.txt \
  --output-cpp cpp.nii.gz \
  --output-result result.nii.gz
```

Common options:

| Option | Short | Description |
|--------|-------|-------------|
| `--reference` | `-r` | Reference image |
| `--floating` | `-f` | Floating image |
| `--output-result` | `-o` | Resampled output image |
| `--output-cpp` | `-c` | Output control point grid |
| `--input-affine` | `-i` | Input affine transformation |
| `--input-cpp` | | Input control point grid |
| `--reference-mask` | `-m` | Mask in reference space |
| `--bending-energy-weight` | | Bending energy penalty weight |
| `--spacing-x` | | Control point spacing in x (mm) |

## `measure`

Compute similarity measures between two images.

```shell
niftyregw measure \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --ncc
```

Options:

| Option | Description |
|--------|-------------|
| `--reference` | Reference image |
| `--floating` | Floating image |
| `--ncc` | Normalized cross-correlation |
| `--nmi` | Normalized mutual information |
| `--ssd` | Sum of squared differences |
| `--lncc` | LNCC (windowed) |

## `resample`

Resample a floating image into the reference space using a transformation.

```shell
niftyregw resample \
  --reference ref.nii.gz \
  --floating flo.nii.gz \
  --transformation trans.nii.gz \
  --output-result result.nii.gz
```

## `jacobian`

Compute Jacobian-based maps (determinant, log determinant, matrix) from a
transformation.

```shell
niftyregw jacobian \
  --reference ref.nii.gz \
  --transformation trans.nii.gz \
  --output-jacobian-determinant jac_det.nii.gz
```

## `tools`

Miscellaneous image manipulation utilities.

```shell
niftyregw tools \
  --input image.nii.gz \
  --output-float image_float.nii.gz
```

## `average`

Average images or transformations. This subcommand has multiple modes:

```shell
niftyregw average --help
```

| Subcommand | Description |
|------------|-------------|
| `avg` | Average images or affine matrices |
| `avg-lts` | Robust average of affine matrices (LTS) |
| `avg-tran` | Resample all images and average |
| `demean` | Demean transformations |
| `demean-noaff` | Demean with affine removal |
| `cmd-file` | Run from a command file |

### Example

```shell
niftyregw average avg \
  --output mean.nii.gz \
  img1.nii.gz img2.nii.gz img3.nii.gz
```

## `transform`

Manipulate and compose transformations. This subcommand has multiple modes:

```shell
niftyregw transform --help
```

| Subcommand | Description |
|------------|-------------|
| `deformation` | Compute a deformation field |
| `displacement` | Compute a displacement field |
| `flow` | Compute a flow field from SVF |
| `compose` | Compose two transformations |
| `landmarks` | Apply transformation to landmarks |
| `update-sform` | Update image sform with affine |
| `invert-affine` | Invert an affine matrix |
| `invert-nonrigid` | Invert a non-rigid transformation |
| `half` | Halve a transformation |
| `make-affine` | Create affine from parameters |
| `affine-to-rigid` | Extract rigid from affine |
| `flirt-to-niftyreg` | Convert FSL FLIRT to NiftyReg affine |

### Examples

```shell
# Compose two transformations
niftyregw transform compose \
  --first affine.txt \
  --second cpp.nii.gz \
  --reference ref.nii.gz \
  --output composed.nii.gz

# Invert an affine
niftyregw transform invert-affine \
  --input affine.txt \
  --output affine_inv.txt
```
