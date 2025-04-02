"""Tests for strain data analysis module."""

import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt

from strain_analysis_data import (
    format_scientific,
    calculate_regression,
    analyze_strain_data,
    create_strain_plot,
    create_strain_dataframe,
    export_raw_data,
    export_analysis_results,
    export_data,
)


def test_format_scientific():
    """Test scientific number formatting."""
    # Test very large number
    large_value = np.array(1.23e6)
    expected_large = "{:.2e}".format(float(large_value))
    assert format_scientific(large_value) == expected_large

    # Test regular number with unit
    regular_value = np.array(1.23)
    expected_regular = "{:.2e}".format(float(regular_value))
    assert format_scientific(regular_value, "mm") == f"{expected_regular} mm"

    # Test regular number with trailing zeros
    trailing_value = np.array(1.230000)
    expected_trailing = "{:.2e}".format(float(trailing_value))
    assert format_scientific(trailing_value) == expected_trailing

    # Test zero
    zero_value = np.array(0.0)
    expected_zero = "{:.2e}".format(float(zero_value))
    assert format_scientific(zero_value) == expected_zero
    assert format_scientific(zero_value, "mm") == f"{expected_zero} mm"

    # Test very small number
    small_value = np.array(1.23e-6)
    expected_small = "{:.2e}".format(float(small_value))
    assert format_scientific(small_value) == expected_small


def test_calculate_regression():
    """Test regression calculation."""
    x_values = [0, 1, 2, 3, 4]
    y_values = [0, 2, 4, 6, 8]  # Perfect linear relationship

    result = calculate_regression(x_values, y_values)
    assert isinstance(result, dict)
    assert np.isclose(result["slope"], 2.0)
    assert np.isclose(result["intercept"], 0.0)
    assert np.isclose(result["r_squared"], 1.0)
    assert result["p_value"] < 0.05


def test_analyze_strain_data():
    """Test strain data analysis."""
    # Create sample strain data
    strain_data = [
        {
            "filename": "test1.jpg",
            "deformation_distance": 0.0,
            "strain_tensor": np.array([[0.0, 0.0], [0.0, 0.0]]),
        },
        {
            "filename": "test2.jpg",
            "deformation_distance": 1.0,
            "strain_tensor": np.array([[0.1, 0.05], [0.05, 0.1]]),
        },
    ]
    scale_length = 10.0

    results = analyze_strain_data(strain_data, scale_length)
    assert isinstance(results, dict)
    assert "strain_data" in results
    assert "scale_length" in results
    assert "regression_results" in results
    assert all(
        axis in results["regression_results"] for axis in ["x_axis", "y_axis", "shear"]
    )


def test_create_strain_plot():
    """Test strain plot creation."""
    x_values = [0, 1, 2]
    y_values = [0, 1, 2]
    results = {
        "slope": 1.0,
        "intercept": 0.0,
        "r_squared": 1.0,
        "p_value": 0.0,
    }

    fig = create_strain_plot(x_values, y_values, results, "Test Plot", "Strain")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_create_strain_dataframe():
    """Test strain DataFrame creation."""
    x_values = [0, 1, 2]
    y_values = [0, 1, 2]
    strain_type = "εxx"

    df = create_strain_dataframe(x_values, y_values, strain_type)
    assert isinstance(df, pd.DataFrame)
    assert "Distance (mm)" in df.columns
    assert strain_type in df.columns
    assert len(df) == 3


def test_export_raw_data():
    """Test raw data export."""
    files_data = {"test.jpg": {"points": []}}
    scale_length = 10.0
    strain_data = [
        {
            "filename": "test.jpg",
            "deformation_distance": 0.0,
            "strain_tensor": np.array([[0.0, 0.0], [0.0, 0.0]]),
        }
    ]

    json_str, csv_str = export_raw_data(files_data, scale_length, strain_data)
    assert isinstance(json_str, str)
    assert isinstance(csv_str, str)
    assert "test.jpg" in json_str
    assert "test.jpg" in csv_str


def test_export_analysis_results():
    """Test analysis results export."""
    regression_results = {
        "x_axis": {
            "slope": 1.0,
            "intercept": 0.0,
            "r_squared": 1.0,
            "p_value": 0.0,
        },
        "y_axis": {
            "slope": 1.0,
            "intercept": 0.0,
            "r_squared": 1.0,
            "p_value": 0.0,
        },
        "shear": {
            "slope": 1.0,
            "intercept": 0.0,
            "r_squared": 1.0,
            "p_value": 0.0,
        },
    }

    json_str, csv_str = export_analysis_results(regression_results)
    assert isinstance(json_str, str)
    assert isinstance(csv_str, str)
    assert "x_axis" in json_str
    assert "x_axis" in csv_str


def test_export_data_unsupported_format():
    """Test export_data with unsupported format."""
    data = {"test": "data"}
    with pytest.raises(ValueError, match="Unsupported format"):
        export_data(data, format="invalid")
