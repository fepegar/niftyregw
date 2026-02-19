"""Tests for niftyregw.__init__ module."""

import niftyregw


def test_version_exists():
    """Test that __version__ is defined."""
    assert hasattr(niftyregw, "__version__")
    assert isinstance(niftyregw.__version__, str)


def test_package_name():
    """Test that __package__ is defined."""
    assert niftyregw.__package__ == "niftyregw"


def test_exported_functions():
    """Test that expected functions are exported."""
    assert hasattr(niftyregw, "download_niftyreg")
    assert hasattr(niftyregw, "reg_aladin")
    assert hasattr(niftyregw, "run")


def test_all_exports():
    """Test __all__ contains expected exports."""
    assert "download_niftyreg" in niftyregw.__all__
    assert "reg_aladin" in niftyregw.__all__
    assert "run" in niftyregw.__all__
    assert len(niftyregw.__all__) == 3


def test_callable_exports():
    """Test that exported items are callable."""
    assert callable(niftyregw.download_niftyreg)
    assert callable(niftyregw.reg_aladin)
    assert callable(niftyregw.run)
