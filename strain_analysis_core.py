"""Core strain analysis module.

This module provides fundamental functions for strain tensor calculation and point normalization.
It is designed to be simple and focused on the core mathematical operations.
"""

import numpy as np
from typing import Literal, Tuple


def validate_points(
    points: np.ndarray, expected_shape: Tuple[int, int], name: str
) -> None:
    """Validate point array shape.

    Args:
        points: Array to validate
        expected_shape: Expected shape as (rows, cols)
        name: Name of the array for error messages
    """
    if points.shape != expected_shape:
        raise ValueError(f"{name} must be an array of shape {expected_shape}")


def normalize_points_by_scale(
    fiducial_points: np.ndarray, scale_points: np.ndarray, scale_length: float
) -> np.ndarray:
    """Normalize points with respect to scale length.

    Args:
        fiducial_points: Array of shape (5,2) with (x,y) coordinates of fiducial markers
        scale_points: Array of shape (2,2) with (x,y) coordinates of scale markers
        scale_length: Physical length of the scale in real-world units

    Returns:
        Normalized fiducial points array of shape (5,2)
    """
    # Validate inputs
    validate_points(fiducial_points, (5, 2), "fiducial_points")
    validate_points(scale_points, (2, 2), "scale_points")

    # Calculate scale factor
    pixel_scale = np.linalg.norm(scale_points[1] - scale_points[0])
    scale_factor = scale_length / pixel_scale

    # Normalize points
    return (fiducial_points - scale_points[0]) * scale_factor


def calculate_strain_tensor(
    original_points: np.ndarray,
    deformed_points: np.ndarray,
    strain_type: Literal["small", "green_lagrangian"] = "small",
    center_index: int = 4,
) -> np.ndarray:
    """Calculate 2D strain tensor from 5 fiducial markers.

    Point configuration:
    0: top-left corner
    1: top-right corner
    2: bottom-right corner
    3: bottom-left corner
    4: center point

    Args:
        original_points: Array of shape (5,2) with (x,y) coordinates before deformation
        deformed_points: Array of shape (5,2) with (x,y) coordinates after deformation
        strain_type: "small" for infinitesimal strain or "green_lagrangian" for large deformations
        center_index: Index of the center point (default is 4)

    Returns:
        2x2 numpy array representing the strain tensor:
        [[εxx, εxy],
         [εxy, εyy]]
    """
    # Validate inputs
    original_points = np.asarray(original_points, dtype=float)
    deformed_points = np.asarray(deformed_points, dtype=float)
    validate_points(original_points, (5, 2), "original_points")
    validate_points(deformed_points, (5, 2), "deformed_points")

    if center_index < 0 or center_index >= len(original_points):
        raise ValueError(
            f"center_index must be between 0 and {len(original_points) - 1}"
        )

    # Extract center points and calculate vectors
    center_original = original_points[center_index]
    center_deformed = deformed_points[center_index]
    corner_indices = [i for i in range(len(original_points)) if i != center_index]

    # Calculate vectors from center to corner points
    vectors_original = (
        original_points[corner_indices] - center_original
    )  # Shape: (4, 2)
    vectors_deformed = (
        deformed_points[corner_indices] - center_deformed
    )  # Shape: (4, 2)

    # Calculate deformation gradient using least squares
    # We need to solve: vectors_deformed = F @ vectors_original.T
    # This is equivalent to: vectors_deformed.T = vectors_original @ F.T
    F_transpose, _, rank, _ = np.linalg.lstsq(
        vectors_original,  # Shape: (4, 2)
        vectors_deformed,  # Shape: (4, 2)
        rcond=None,
    )
    F = F_transpose.T  # Shape: (2, 2)

    if rank < 2:
        print("Warning: Solution may be inaccurate due to point configuration")

    # Calculate strain tensor
    identity_matrix = np.eye(2)
    if strain_type == "small":
        # Small deformation (infinitesimal) strain
        return 0.5 * (F + F.T) - identity_matrix
    else:  # green_lagrangian
        # Green-Lagrangian strain (for large deformations)
        return 0.5 * (F.T @ F - identity_matrix)
