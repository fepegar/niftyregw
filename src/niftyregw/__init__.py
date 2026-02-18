from importlib.metadata import version

from .wrapper import reg_aladin, run

__all__ = [
    "reg_aladin",
    "run",
]

assert __package__ is not None
__version__ = version(__package__)
