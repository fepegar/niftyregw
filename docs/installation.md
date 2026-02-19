# Installation

## Install niftyregw

=== "pip"

    ```shell
    pip install niftyregw
    ```

=== "uv"

    ```shell
    uv pip install niftyregw
    ```

=== "As a CLI tool"

    ```shell
    uv tool install niftyregw
    ```

## Install NiftyReg

`niftyregw` requires the NiftyReg binaries to be available on your `PATH`.
You can install them from the
[NiftyReg releases page](https://github.com/KCL-BMEIS/niftyreg/releases).

Download the appropriate archive for your platform, extract it, and ensure the
binaries (e.g., `reg_aladin`, `reg_f3d`) are on your `PATH`.

### Verify the installation

```shell
niftyregw aladin --version
```

!!! note "Supported platforms"

    NiftyReg provides pre-built binaries for:

    - **Linux** (Ubuntu, with optional CUDA support)
    - **macOS** (Apple Silicon and Intel)
    - **Windows** (with optional CUDA support)
