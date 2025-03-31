import numpy as np
import pytest
from strain_analysis import normalize_points_by_scale, calculate_strain_tensor


def test_normalize_points_by_scale():
    # Test case 1: Simple scaling
    fiducial_points = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
    scale_points = np.array([[0, 0], [1, 0]])
    scale_length = 10.0

    normalized = normalize_points_by_scale(fiducial_points, scale_points, scale_length)

    # Check if scale points are correctly normalized
    assert np.isclose(normalized[0, 0], 0.0)  # First point should be at origin
    assert np.isclose(normalized[1, 0], 10.0)  # Second point should be at scale_length

    # Test case 2: Different scale points
    scale_points = np.array([[1, 1], [2, 1]])
    normalized = normalize_points_by_scale(fiducial_points, scale_points, scale_length)
    assert np.isclose(
        normalized[0, 0], -10.0
    )  # First point should be shifted left by scale_length

    # Test case 3: Invalid input shapes
    with pytest.raises(ValueError):
        normalize_points_by_scale(fiducial_points, np.array([[0, 0]]), scale_length)


def test_calculate_strain_tensor():
    # Test case 1: No deformation
    original = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
    deformed = original.copy()

    strain = calculate_strain_tensor(original, deformed)
    assert np.allclose(strain, np.zeros((2, 2)))

    # Test case 2: Simple extension in x-direction
    deformed = original.copy()
    deformed[:, 0] *= 1.2  # 20% extension in x-direction
    strain = calculate_strain_tensor(original, deformed)
    assert np.isclose(strain[0, 0], 0.2)  # εxx should be 0.2
    assert np.isclose(strain[1, 1], 0.0)  # εyy should be 0

    # Test case 3: Different center point
    strain = calculate_strain_tensor(original, deformed, center_index=0)
    assert not np.allclose(strain, np.zeros((2, 2)))

    # Test case 4: Different strain types
    strain_small = calculate_strain_tensor(original, deformed, strain_type="small")
    strain_large = calculate_strain_tensor(
        original, deformed, strain_type="green_lagrangian"
    )
    assert not np.allclose(strain_small, strain_large)

    # Test case 5: Invalid inputs
    with pytest.raises(ValueError):
        calculate_strain_tensor(original, deformed[:4])  # Different shapes

    with pytest.raises(ValueError):
        calculate_strain_tensor(
            original, deformed, center_index=5
        )  # Invalid center index
