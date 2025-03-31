import numpy as np
from typing import Literal


def normalize_points_by_scale(
    fiducial_points: np.ndarray, scale_points: np.ndarray, scale_length: float
) -> np.ndarray:
    """
    Normalize points with respect to scale length to account for image scaling.

    Args:
        fiducial_points: Array of shape (5,2) with (x,y) coordinates of fiducial markers
        scale_points: Array of shape (2,2) with (x,y) coordinates of scale markers
        scale_length: Physical length of the scale in real-world units

    Returns:
        Normalized fiducial points array of shape (5,2)
    """
    # Validate input shapes
    if fiducial_points.shape != (5, 2):
        raise ValueError(
            "fiducial_points must be an array of shape (5,2) with exactly 5 points"
        )
    if scale_points.shape != (2, 2):
        raise ValueError(
            "scale_points must be an array of shape (2,2) with exactly 2 points"
        )

    # Calculate pixel distance between scale points
    pixel_scale = np.linalg.norm(scale_points[1] - scale_points[0])

    # Calculate scale factor (real-world units per pixel)
    scale_factor = scale_length / pixel_scale

    # Normalize all points by subtracting the first scale point and scaling
    normalized_points = (fiducial_points - scale_points[0]) * scale_factor

    return normalized_points


def calculate_strain_tensor(
    original_points: np.ndarray,
    deformed_points: np.ndarray,
    strain_type: Literal["small", "green_lagrangian"] = "small",
    center_index: int = 4,
) -> np.ndarray:
    """
    Calculate 2D strain tensor from 5 fiducial markers before and after deformation.

    The standard 5-point configuration should be ordered as:
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
    # Convert inputs to numpy arrays
    original_points = np.asarray(original_points, dtype=float)
    deformed_points = np.asarray(deformed_points, dtype=float)

    # Validate input
    if original_points.shape != deformed_points.shape:
        raise ValueError("Point arrays must have the same shape")

    if center_index < 0 or center_index >= len(original_points):
        raise ValueError(
            f"center_index must be between 0 and {len(original_points) - 1}"
        )

    # Extract center point
    center_original = original_points[center_index]
    center_deformed = deformed_points[center_index]

    # Get indices of corner points (all points except the center)
    corner_indices = [i for i in range(len(original_points)) if i != center_index]

    # Calculate vectors from center to corner points
    vectors_original = original_points[corner_indices] - center_original
    vectors_deformed = deformed_points[corner_indices] - center_deformed

    # Prepare matrices for deformation gradient calculation
    V = vectors_original.T  # 2×N matrix where each column is a vector
    V_prime = vectors_deformed.T  # 2×N matrix

    # Calculate deformation gradient F using least squares
    F_transpose, _, rank, _ = np.linalg.lstsq(V.T, V_prime.T, rcond=None)
    F = F_transpose.T

    # Check solution quality
    if rank < 2:
        print("Warning: Solution may be inaccurate due to point configuration")

    # Calculate strain tensor based on specified type
    identity_matrix = np.eye(2)

    if strain_type == "small":
        # Small deformation (infinitesimal) strain
        strain_tensor = 0.5 * (F + F.T) - identity_matrix
    else:
        # Green-Lagrangian strain (for large deformations)
        strain_tensor = 0.5 * (F.T @ F - identity_matrix)

    return strain_tensor
