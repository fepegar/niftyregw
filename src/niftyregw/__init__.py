from importlib.metadata import version

from .wrapper import reg_aladin

__all__ = [
    "reg_aladin",
]

assert __package__ is not None
__version__ = version(__package__)
