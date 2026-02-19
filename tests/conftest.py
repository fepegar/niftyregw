"""Shared pytest fixtures and configuration."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path_factory_session(tmp_path_factory):
    """Provide a tmp_path_factory for session-scoped fixtures."""
    return tmp_path_factory


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_nifti_image(temp_dir):
    """Create a mock NIfTI image file."""
    image_path = temp_dir / "test_image.nii.gz"
    image_path.touch()
    return image_path


@pytest.fixture
def mock_affine_file(temp_dir):
    """Create a mock affine transformation file."""
    affine_path = temp_dir / "test_affine.txt"
    affine_path.write_text("1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n")
    return affine_path
