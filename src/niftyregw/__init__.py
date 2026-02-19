from importlib.metadata import version

from .install import download_niftyreg
from .wrapper import reg_aladin, run

__all__ = [
    "download_niftyreg",
    "reg_aladin",
    "run",
]

assert __package__ is not None
__version__ = version(__package__)
