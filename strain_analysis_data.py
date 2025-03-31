"""Data analysis and visualization module for strain analysis.

This module provides functions for analyzing strain data, performing regression,
and creating visualizations. It is designed to be easily extensible for researchers
to add their own analysis methods.
"""

from typing import Dict, List, TypedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import json


class StrainData(TypedDict):
    """Type definition for strain data."""

    filename: str
    deformation_distance: float
    strain_tensor: np.ndarray


class RegressionResult(TypedDict):
    """Type definition for regression results."""

    slope: float
    intercept: float
    r_squared: float
    p_value: float


class AnalysisResults(TypedDict):
    """Type definition for complete analysis results."""

    strain_data: List[StrainData]
    scale_length: float
    regression_results: Dict[str, RegressionResult]


def format_scientific(value: float, unit: str = "") -> str:
    """Format numbers in scientific notation for readability.

    Args:
        value: The number to format (can be float or numpy array)
        unit: Optional unit to append to the formatted number

    Returns:
        str: Formatted number in scientific notation with optional unit
    """
    value_float = float(value.item() if isinstance(value, np.ndarray) else value)
    return f"{value_float:.2e} {unit}".strip()


def calculate_regression(
    x_values: List[float], y_values: List[float]
) -> RegressionResult:
    """Calculate linear regression for a set of x and y values.

    Args:
        x_values: List of x values (e.g., deformation distances)
        y_values: List of y values (e.g., strain components)

    Returns:
        RegressionResult containing slope, intercept, R², and p-value
    """
    slope, intercept, r_value, p_value, _ = stats.linregress(x_values, y_values)
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value**2),
        "p_value": float(p_value),
    }


def analyze_strain_data(
    strain_data: List[StrainData], scale_length: float
) -> AnalysisResults:
    """Analyze strain data and calculate regression results.

    Args:
        strain_data: List of strain data points
        scale_length: Physical length of the scale in real-world units

    Returns:
        AnalysisResults containing strain data and regression results
    """
    x_values = [d["deformation_distance"] for d in strain_data]
    strain_components = {"x_axis": (0, 0), "y_axis": (1, 1), "shear": (0, 1)}

    regression_results = {
        name: calculate_regression(
            x_values, [d["strain_tensor"][i, j] for d in strain_data]
        )
        for name, (i, j) in strain_components.items()
    }

    return {
        "strain_data": strain_data,
        "scale_length": scale_length,
        "regression_results": regression_results,
    }


def create_strain_plot(
    x_values: List[float],
    y_values: List[float],
    results: RegressionResult,
    title: str,
    ylabel: str,
) -> plt.Figure:
    """Create a plot for strain data with regression line.

    Args:
        x_values: List of x values (deformation distances)
        y_values: List of y values (strain components)
        results: Regression results
        title: Plot title
        ylabel: Y-axis label

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, color="blue", label="Data points")
    ax.plot(
        x_values,
        [results["slope"] * x + results["intercept"] for x in x_values],
        color="red",
        label="Regression line",
    )
    ax.set_xlabel("Deformation Distance (mm)")
    ax.set_ylabel(ylabel)
    ax.legend()
    return fig


def create_strain_dataframe(
    x_values: List[float], y_values: List[float], strain_type: str
) -> pd.DataFrame:
    """Create a DataFrame for strain data.

    Args:
        x_values: List of x values (deformation distances)
        y_values: List of y values (strain components)
        strain_type: Type of strain (e.g., "εxx", "εyy", "εxy")

    Returns:
        pandas DataFrame with formatted data
    """
    return pd.DataFrame(
        {
            "Distance (mm)": [f"{x:.2f}" for x in x_values],
            strain_type: [format_scientific(y, "") for y in y_values],
        }
    )


def export_data(data: Dict, format: str = "json") -> str:
    """Export data in specified format."""
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "csv":
        return pd.DataFrame(data).to_csv(index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")


def export_raw_data(
    files_data: Dict, scale_length: float, strain_data: List[StrainData]
) -> tuple[str, str]:
    """Export raw data in JSON and CSV formats.

    Args:
        files_data: Dictionary containing file data
        scale_length: Physical length of the scale
        strain_data: List of strain data points

    Returns:
        Tuple of (json_str, csv_str) containing formatted data
    """
    # JSON format
    raw_data = {
        "files_data": files_data,
        "scale_length": scale_length,
    }
    json_str = export_data(raw_data, "json")

    # CSV format
    csv_data = [
        {
            "filename": data["filename"],
            "deformation_distance": data["deformation_distance"],
            "strain_xx": data["strain_tensor"][0, 0],
            "strain_yy": data["strain_tensor"][1, 1],
            "strain_xy": data["strain_tensor"][0, 1],
        }
        for data in strain_data
    ]
    csv_str = export_data(csv_data, "csv")

    return json_str, csv_str


def export_analysis_results(
    regression_results: Dict[str, RegressionResult],
) -> tuple[str, str]:
    """Export analysis results in JSON and CSV formats.

    Args:
        regression_results: Dictionary containing regression results

    Returns:
        Tuple of (json_str, csv_str) containing formatted results
    """
    # JSON format
    json_str = export_data(regression_results, "json")

    # CSV format
    analysis_data = [
        {"component": name, **results} for name, results in regression_results.items()
    ]
    csv_str = export_data(analysis_data, "csv")

    return json_str, csv_str
