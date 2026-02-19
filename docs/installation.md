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
The easiest way is to use the built-in `install` command:

```shell
niftyregw install
```

This downloads the correct pre-built NiftyReg binaries for your platform and
places them in `~/.local/bin` by default.

To install to a custom directory:

```shell
niftyregw install --output-dir /opt/niftyreg/bin
```

Or from Python:

```python
from niftyregw import download_niftyreg

download_niftyreg()  # ~/.local/bin
download_niftyreg("/opt/niftyreg/bin")  # custom directory
```

!!! warning "Ensure the directory is on your `PATH`"

    If `~/.local/bin` is not already on your `PATH`, add it:

    ```shell
    export PATH="$HOME/.local/bin:$PATH"
    ```

    Add this line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Verify the installation

```shell
niftyregw aladin --version
```

!!! note "Supported platforms"

    NiftyReg provides pre-built binaries for:

    - **Linux** (Ubuntu, with optional CUDA support)
    - **macOS** (Apple Silicon and Intel)
    - **Windows** (with optional CUDA support)
