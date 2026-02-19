---
icon: lucide/heart-pulse
---

# niftyregw

Pythonic wrapper for [NiftyReg](https://github.com/KCL-BMEIS/niftyreg),
providing a modern CLI and Python API for medical image registration.

[NiftyReg](https://github.com/KCL-BMEIS/niftyreg) is a suite of tools for
efficient medical image registration developed at
[King's College London](https://www.kcl.ac.uk/).

---

## Features

- :material-console: **Modern CLI** — Typer-based CLI with descriptive option
  names for all 8 NiftyReg binaries
- :material-language-python: **Python API** — Call registration tools directly
  from Python with typed arguments
- :material-file-tree: **Structured logging** — Loguru-based logging with
  NiftyReg output classification
- :material-download: **Easy installation** — Install via `pip` or `uv`, with
  automatic NiftyReg binary discovery

## Quick start

=== "CLI"

    ```shell
    pip install niftyregw
    niftyregw aladin \
      --reference ref.nii.gz \
      --floating flo.nii.gz \
      --output-result result.nii.gz
    ```

=== "Python"

    ```python
    from niftyregw import reg_aladin

    reg_aladin(
        reference="ref.nii.gz",
        floating="flo.nii.gz",
        output_result="result.nii.gz",
    )
    ```

!!! tip "Looking for NiftyReg binaries?"

    `niftyregw` expects NiftyReg binaries (e.g., `reg_aladin`) to be available
    on your `PATH`. See [Installation](installation.md) for details.
