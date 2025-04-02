"""UI components and visualization module for strain analysis.

This module provides functions for creating the Streamlit interface, handling user interactions,
and displaying results. It is designed to be easily extensible for researchers to add their own
visualization and export methods.
"""

from typing import Dict, List, TypedDict, Optional
import os
import streamlit as st
import pandas as pd

from strain_analysis_data import (
    StrainData,
    RegressionResult,
    create_strain_plot,
    create_strain_dataframe,
    export_raw_data,
    export_analysis_results,
    format_scientific,
)


# Type definitions
class Point(TypedDict):
    point: List[float]  # [x, y] coordinates
    label: str  # 'Fiducial' or 'Scale'
    label_id: int  # 0 for Fiducial, 1 for Scale


class FileData(TypedDict):
    id: str
    filename: str
    order: int
    points: List[Point]
    status: tuple[bool, str]  # (is_valid, status_message)
    deformation_distance: Optional[float]


# Constants
TEMP_DIR = os.path.expanduser("~/tmp")
TEMP_IMAGE_PATH = os.path.join(TEMP_DIR, "temp_image.jpg")
os.makedirs(TEMP_DIR, exist_ok=True)

# UI Configuration
PAGE_CONFIG = {
    "page_title": "Strain Seer - 2D Strain Analysis Tool",
    "page_icon": "👁️",
    "layout": "wide",
}

STATUS_COLORS = {
    "Complete": "color: green",
    "Incomplete": "color: orange",
    "Missing Distance": "color: purple",
    "Missing": "color: red",
}

POINT_COLORS = {"Fiducial": "color: red", "Scale": "color: green"}


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(**PAGE_CONFIG)


def initialize_session_state():
    """Initialize session state variables."""
    if "files_data" not in st.session_state:
        st.session_state.files_data = {}
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "last_scale_length" not in st.session_state:
        st.session_state.last_scale_length = 10.0


def validate_annotation(
    points: List[Point], deformation_distance: Optional[float]
) -> tuple[bool, str]:
    """Validate annotation completeness and correctness."""
    if not points:
        return False, "Missing"

    fiducial_count = sum(1 for p in points if p["label"] == "Fiducial")
    scale_count = sum(1 for p in points if p["label"] == "Scale")

    if fiducial_count != 5 or scale_count != 2:
        return False, "Incomplete"
    if deformation_distance is None:
        return False, "Missing Distance"
    return True, "Complete"


def save_annotation(
    file_id: str,
    filename: str,
    order: int,
    points: Optional[List[Point]] = None,
    deformation_distance: Optional[float] = None,
) -> None:
    """Save or update annotation data in session state."""
    current_data = st.session_state.files_data.get(
        file_id,
        {
            "id": file_id,
            "filename": filename,
            "order": order,
            "points": [],
            "deformation_distance": None,
            "status": (False, "Missing"),
        },
    )

    st.session_state.files_data[file_id] = {
        "id": file_id,
        "filename": filename,
        "order": order,
        "points": points or current_data["points"],
        "deformation_distance": deformation_distance
        if deformation_distance is not None
        else current_data["deformation_distance"],
        "status": validate_annotation(
            points or current_data["points"],
            deformation_distance
            if deformation_distance is not None
            else current_data["deformation_distance"],
        ),
    }


def display_files_table(files_data: Dict[str, FileData]):
    """Display files table with status information."""
    sorted_files = sorted(files_data.values(), key=lambda x: x["order"])

    files_df = pd.DataFrame(
        [
            {
                "Order": data["order"] + 1,
                "File": data["filename"],
                "Status": data["status"][1],
                "Fiducial Points": sum(
                    1 for p in data["points"] if p["label"] == "Fiducial"
                ),
                "Scale Points": sum(1 for p in data["points"] if p["label"] == "Scale"),
                "Deformation Distance (mm)": data["deformation_distance"]
                if data["deformation_distance"] is not None
                else None,
            }
            for data in sorted_files
        ]
    )

    st.markdown("### 📊 Files Status")
    st.dataframe(
        files_df.style.map(
            lambda x: STATUS_COLORS.get(x, "color: red"), subset=["Status"]
        ),
        hide_index=True,
    )


def display_point_coordinates(points: List[Point]):
    """Display point coordinates in a table."""
    if points:
        df = pd.DataFrame(
            [
                {
                    "Type": point["label"],
                    "Order": i + 1,
                    "X": f"{point['point'][0]:.1f}",
                    "Y": f"{point['point'][1]:.1f}",
                }
                for i, point in enumerate(points)
            ]
        )

        st.markdown("#### Point Coordinates")
        st.dataframe(
            df.style.map(
                lambda x: POINT_COLORS.get(x, "color: black"), subset=["Type"]
            ),
            hide_index=True,
        )


def display_strain_component(
    x_values: List[float],
    y_values: List[float],
    results: RegressionResult,
    title: str,
    ylabel: str,
):
    """Display a single strain component with plot and data."""
    st.markdown(f"### 📈 {title}")

    # Create and display plot
    fig = create_strain_plot(x_values, y_values, results, title, ylabel)
    st.pyplot(fig)

    # Display regression info
    st.markdown(f"""
    **Regression Equation:**  
    {ylabel} = {format_scientific(results["slope"], "mm⁻¹")}x + {format_scientific(results["intercept"], "")}
    
    **R² Value:** {format_scientific(results["r_squared"], "")}
    **P-value:** {format_scientific(results["p_value"], "")}
    """)

    # Display data table
    df = create_strain_dataframe(x_values, y_values, ylabel)
    st.dataframe(df)


def display_analysis_results(
    strain_data: List[StrainData],
    regression_results: Dict[str, RegressionResult],
):
    """Display analysis results with plots and tables."""
    x_values = [d["deformation_distance"] for d in strain_data]

    # Create three columns for visualization
    col1, col2, col3 = st.columns(3)

    with col1:
        display_strain_component(
            x_values,
            [d["strain_tensor"][0, 0] for d in strain_data],
            regression_results["x_axis"],
            "X-Axis Strain (εxx)",
            "Strain (εxx)",
        )

    with col2:
        display_strain_component(
            x_values,
            [d["strain_tensor"][1, 1] for d in strain_data],
            regression_results["y_axis"],
            "Y-Axis Strain (εyy)",
            "Strain (εyy)",
        )

    with col3:
        display_strain_component(
            x_values,
            [d["strain_tensor"][0, 1] for d in strain_data],
            regression_results["shear"],
            "Shear Strain (εxy)",
            "Strain (εxy)",
        )


def display_export_section(
    files_data: Dict[str, FileData],
    scale_length: float,
    strain_data: List[StrainData],
    regression_results: Dict[str, RegressionResult],
):
    """Display data export section with download buttons."""
    st.markdown("---")
    st.markdown("### 📥 Data Export")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Raw Data")
        st.markdown("""
        Available formats:
        - JSON: File data + scale length
        - CSV: Strain components
        """)

        json_str, csv_str = export_raw_data(files_data, scale_length, strain_data)
        st.download_button(
            "Download Raw Data (JSON)",
            json_str,
            file_name="raw_data.json",
            mime="application/json",
        )
        st.download_button(
            "Download Raw Data (CSV)",
            csv_str,
            file_name="raw_data.csv",
            mime="text/csv",
        )

    with col2:
        st.markdown("#### 📊 Analysis Results")
        st.markdown("""
        Available formats:
        - JSON: Regression parameters
        - CSV: Regression data
        """)

        json_str, csv_str = export_analysis_results(regression_results)
        st.download_button(
            "Download Analysis Results (JSON)",
            json_str,
            file_name="analysis_results.json",
            mime="application/json",
        )
        st.download_button(
            "Download Analysis Results (CSV)",
            csv_str,
            file_name="analysis_results.csv",
            mime="text/csv",
        )


def cleanup_temp_files():
    """Clean up temporary files to prevent disk space issues."""
    if os.path.exists(TEMP_IMAGE_PATH):
        os.remove(TEMP_IMAGE_PATH)
