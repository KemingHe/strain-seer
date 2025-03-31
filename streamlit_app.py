# Standard library imports
import json
import os
from typing import Dict, List, TypedDict, Optional
import uuid

# Third-party library imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from scipy import stats
import streamlit as st
from streamlit_image_annotation import pointdet

# Local application imports
from strain_analysis import normalize_points_by_scale, calculate_strain_tensor

# Configure Streamlit page with favicon and wide layout for better visualization
st.set_page_config(
    page_title="Strain Seer - 2D Strain Analysis Tool", page_icon="📍", layout="wide"
)

# Initialize session state to persist data between reruns
# Using session state ensures data survives page refreshes and maintains user progress
if "files_data" not in st.session_state:
    st.session_state.files_data = {}
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "last_scale_length" not in st.session_state:
    st.session_state.last_scale_length = 10.0

# Privacy notice to inform users about local data storage
st.info(
    "🔒 Your work is saved locally in this browser tab - remember to export your data before closing"
)


# Type definitions for better code maintainability and IDE support
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


class AnalysisResults(TypedDict):
    strain_data: List[Dict]
    scale_length: float
    regression_results: Dict[str, Dict]


# Configure temporary file handling for image processing
TEMP_DIR = os.path.expanduser("~/tmp")
TEMP_IMAGE_PATH = os.path.join(TEMP_DIR, "temp_image.jpg")
os.makedirs(TEMP_DIR, exist_ok=True)

# Title and description
st.title("Strain Seer - 2D Strain Analysis Tool")

# Main description
st.markdown("""
## 📊 What is 2D Strain Analysis?

2D strain analysis measures material deformation using 5 fiducial markers and 2 scale markers to calculate:
- εxx: Stretching/compression in x-direction
- εyy: Stretching/compression in y-direction
- εxy: Shearing deformation

### 🔄 How It Works

1. Mark 5 fiducial points (red) and 2 scale points (green)
2. Enter scale length to convert pixels to real-world units
3. Input deformation distance for each image
4. View strain analysis and regression results

### 📍 Point Labeling & Scale

```text
0 ------- 1
|  \\   /  |
|    4    |
|  /   \\  |
3 ------- 2
```

- Points 0-3: Corner points (clockwise from top-left)
- Point 4: Center point
- Scale points: Calibration markers (green)

Scale points ensure consistent measurements across images and accurate pixel-to-real-world conversion. For example:

```text
Image 1 (1000px)     Image 2 (2000px)
+----------------+   +------------------------+
|                |   |                        |
|  [10mm]        |   |    [10mm]              |
|  |----|        |   |    |----|              |
|                |   |                        |
+----------------+   +------------------------+

Without Scale:           With Scale:
- 100px = ?mm          - 100px = 1mm
- 200px = ?mm          - 200px = 1mm
```
""")

# Create two columns for Quick Start Guide and Tips
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🚀 Quick Start Guide

    1. **Upload Images** (PNG, JPG, JPEG, GIF, BMP)
       - Upload files in order (minimum 3 for reliable analysis)
       - Order determines sequence in analysis and plots

    2. **Annotate Points**
       - Mark 5 red fiducial points and 2 green scale points
       - Enter deformation distance for each image

    3. **Run Analysis**
       - Set scale length
       - View results
       - Export data
    """)

with col2:
    st.markdown("""
    ### 💡 Tips for Best Results

    - Clear fiducial markers and known scale distance
    - Well-lit, focused images with correct point order (0-4)
    - Upload 3+ images in sequence for reliable analysis
    """)

# Define label list with colors
label_list = ["Fiducial", "Scale"]


def validate_annotation(
    points: List[Point], deformation_distance: Optional[float]
) -> tuple[bool, str]:
    """Validate annotation completeness and correctness.

    Returns:
        tuple[bool, str]: (is_valid, status_message)
        - is_valid: True if all required points are present and deformation distance is set
        - status_message: Human-readable status description
    """
    if not points:
        return False, "Missing"

    # Count point types to ensure correct number of each
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
    """Save or update annotation data in session state.

    Args:
        file_id: Unique identifier for the file
        filename: Original filename
        order: Sequence order for analysis
        points: Optional list of annotated points
        deformation_distance: Optional deformation distance in mm
    """
    # Preserve existing data if updating
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

    # Update only provided fields while preserving others
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


# File uploader
uploaded_files = st.file_uploader(
    "Choose image files",
    type=["png", "jpg", "jpeg", "gif", "bmp"],
    accept_multiple_files=True,
)

# Save uploaded files and initialize their data
for i, uploaded_file in enumerate(uploaded_files):
    # Check if file exists in our data
    file_exists = any(
        data["filename"] == uploaded_file.name
        for data in st.session_state.files_data.values()
    )
    if not file_exists:
        file_id = str(uuid.uuid4())
        save_annotation(file_id, uploaded_file.name, i)

# Display files table with status
if st.session_state.files_data:
    # Sort files by order
    sorted_files = sorted(
        st.session_state.files_data.values(), key=lambda x: x["order"]
    )

    files_df = pd.DataFrame(
        [
            {
                "Order": data["order"] + 1,  # 1-based index for display
                "File": data["filename"],
                "Status": data["status"][1],
                "Fiducial Points": sum(
                    1 for p in data["points"] if p["label"] == "Fiducial"
                ),
                "Scale Points": sum(1 for p in data["points"] if p["label"] == "Scale"),
                "Deformation Distance (mm)": data["deformation_distance"]
                if data["deformation_distance"] is not None
                else "Not Set",
            }
            for data in sorted_files
        ]
    )

    # Color coding for status
    def color_status(val):
        if val == "Complete":
            return "color: green"
        elif val == "Incomplete":
            return "color: orange"
        elif val == "Missing Distance":
            return "color: purple"
        return "color: red"

    st.markdown("### 📊 Files Status")
    st.dataframe(files_df.style.map(color_status, subset=["Status"]), hide_index=True)

    # File selection and annotation section
    st.markdown("### 🎯 Image Annotation")
    selected_filename = st.selectbox(
        "Select image to annotate", options=[data["filename"] for data in sorted_files]
    )

    if selected_filename:
        # Find the file data by filename
        file_data = next(
            data
            for data in st.session_state.files_data.values()
            if data["filename"] == selected_filename
        )

        # Save the image temporarily
        for uploaded_file in uploaded_files:
            if uploaded_file.name == selected_filename:
                with open(TEMP_IMAGE_PATH, "wb") as f:
                    f.write(uploaded_file.getvalue())
                break

        # Get image dimensions
        with Image.open(TEMP_IMAGE_PATH) as img:
            width, height = img.size
            # Calculate dimensions maintaining aspect ratio with minimum size of 512
            scale = max(512 / width, 512 / height)
            display_width = int(width * scale)
            display_height = int(height * scale)

        # Point detection annotation
        points = pointdet(
            TEMP_IMAGE_PATH,
            label_list=label_list,
            points=[[p["point"][0], p["point"][1]] for p in file_data["points"]],
            labels=[0 if p["label"] == "Fiducial" else 1 for p in file_data["points"]],
            height=display_height,
            width=display_width,
            point_width=3,
            use_space=True,
        )

        # Display current annotation table
        if file_data["points"]:
            df_data = []
            for i, point in enumerate(file_data["points"]):
                df_data.append(
                    {
                        "Type": point["label"],
                        "Order": i + 1,
                        "X": f"{point['point'][0]:.1f}",
                        "Y": f"{point['point'][1]:.1f}",
                    }
                )

            df = pd.DataFrame(df_data)

            st.markdown("#### Point Coordinates")
            st.dataframe(
                df.style.map(
                    lambda x: "color: red" if x == "Fiducial" else "color: green",
                    subset=["Type"],
                ),
                hide_index=True,
            )

        # Add deformation distance input after annotation display
        st.markdown("#### Deformation Distance")
        deformation_distance = st.number_input(
            "Enter deformation distance (mm)",
            min_value=0.0,
            value=float(file_data["deformation_distance"])
            if file_data["deformation_distance"] is not None
            else 0.0,
            step=0.1,
            help="Press Enter or click outside to save the value",
        )

        save_annotation(
            file_data["id"],
            file_data["filename"],
            file_data["order"],
            points,
            deformation_distance,
        )

    # Debug section
    # st.markdown("### Debug Information")
    # st.markdown("All files data:")
    # st.json(st.session_state.files_data)

    # Analysis Section
    st.markdown("---")  # Horizontal rule
    st.markdown("## 🔬 Strain Analysis")

    # Check if all files are complete and minimum number of images
    all_complete = all(
        data["status"][0] for data in st.session_state.files_data.values()
    )
    num_images = len(st.session_state.files_data)

    if not all_complete:
        st.warning("""
        ⚠️ **Analysis Disabled**
        
        Complete these steps:
        1. Mark all points (5 fiducial + 2 scale)
        2. Set deformation distance
        3. Verify "Complete" status
        """)
    elif num_images < 3:
        st.warning(f"""
        ⚠️ **Analysis Disabled**
        
        Need more images for reliable analysis:
        - Current: {num_images} image{"s" if num_images != 1 else ""}
        - Required: Minimum 3 images
        - More images provide better regression results
        """)
    else:
        st.success("""
        ✅ **Ready for Analysis**
        
        Next steps:
        1. Set scale length
        2. View results
        3. Export data
        """)

        # Scale length input
        st.markdown("### 📏 Scale Calibration")
        st.markdown("Enter physical length of scale markers (mm)")
        scale_length = st.number_input(
            "Scale Length (mm)",
            min_value=0.0,
            value=st.session_state.last_scale_length,
            step=0.1,
        )

        # Store scale length
        st.session_state.last_scale_length = scale_length

        # Run analysis if scale length changed or no analysis exists
        if (
            st.session_state.analysis_results is None
            or st.session_state.analysis_results["scale_length"] != scale_length
        ):
            # Process all files and calculate strain tensors
            strain_data = []
            for data in sorted_files:
                # Extract points
                fiducial_points = []
                scale_points = []
                for point in data["points"]:
                    if point["label"] == "Fiducial":
                        fiducial_points.append(point["point"])
                    else:
                        scale_points.append(point["point"])

                # Convert to numpy arrays
                fiducial_points = np.array(fiducial_points)
                scale_points = np.array(scale_points)

                # Normalize points
                normalized_points = normalize_points_by_scale(
                    fiducial_points, scale_points, scale_length
                )

                # Calculate strain tensor
                strain_tensor = calculate_strain_tensor(
                    normalized_points, normalized_points
                )  # Using same points for now

                strain_data.append(
                    {
                        "filename": data["filename"],
                        "deformation_distance": data["deformation_distance"],
                        "strain_tensor": strain_tensor,
                    }
                )

            # Calculate regression results
            x_values = [d["deformation_distance"] for d in strain_data]
            regression_results = {}

            # X-axis strain
            y_values = [d["strain_tensor"][0, 0] for d in strain_data]
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_values, y_values
            )
            regression_results["x_axis"] = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value**2),
                "p_value": float(p_value),
            }

            # Y-axis strain
            y_values = [d["strain_tensor"][1, 1] for d in strain_data]
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_values, y_values
            )
            regression_results["y_axis"] = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value**2),
                "p_value": float(p_value),
            }

            # Shear strain
            y_values = [d["strain_tensor"][0, 1] for d in strain_data]
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_values, y_values
            )
            regression_results["shear"] = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value**2),
                "p_value": float(p_value),
            }

            # Store results in session state
            st.session_state.analysis_results = {
                "strain_data": strain_data,
                "scale_length": scale_length,
                "regression_results": regression_results,
            }

        # Display analysis results
        strain_data = st.session_state.analysis_results["strain_data"]
        regression_results = st.session_state.analysis_results["regression_results"]
        x_values = [d["deformation_distance"] for d in strain_data]

        # Create three columns for visualization
        col1, col2, col3 = st.columns(3)

        def format_scientific(value: float, unit: str = "") -> str:
            """Format numbers in scientific notation for better readability of very small/large values.

            Args:
                value: The number to format
                unit: Optional unit to append to the formatted number

            Returns:
                str: Formatted number with optional unit
            """
            if abs(value) < 1e-6 or (abs(value) > 1e6 and value != 0):
                return f"{value:.2e} {unit}"
            return f"{value:.6f} {unit}".rstrip("0").rstrip(".")

        with col1:
            st.markdown("### 📈 X-Axis Strain (εxx)")
            y_values = [d["strain_tensor"][0, 0] for d in strain_data]
            results = regression_results["x_axis"]

            # Create plot
            fig, ax = plt.subplots()
            ax.scatter(x_values, y_values, color="blue", label="Data points")
            ax.plot(
                x_values,
                [results["slope"] * x + results["intercept"] for x in x_values],
                color="red",
                label="Regression line",
            )
            ax.set_xlabel("Deformation Distance (mm)")
            ax.set_ylabel("Strain (εxx)")
            ax.legend()
            st.pyplot(fig)

            # Display regression info with scientific formatting
            st.markdown(f"""
            **Regression Equation:**  
            εxx = {format_scientific(results["slope"], "mm⁻¹")}x + {format_scientific(results["intercept"], "")}
            
            **R² Value:** {format_scientific(results["r_squared"], "")}
            **P-value:** {format_scientific(results["p_value"], "")}
            """)

            # Display data table with scientific formatting
            df_x = pd.DataFrame(
                {
                    "Distance (mm)": [f"{x:.2f}" for x in x_values],
                    "εxx": [format_scientific(y, "") for y in y_values],
                }
            )
            st.dataframe(df_x)

        with col2:
            st.markdown("### 📈 Y-Axis Strain (εyy)")
            y_values = [d["strain_tensor"][1, 1] for d in strain_data]
            results = regression_results["y_axis"]

            # Create plot
            fig, ax = plt.subplots()
            ax.scatter(x_values, y_values, color="blue", label="Data points")
            ax.plot(
                x_values,
                [results["slope"] * x + results["intercept"] for x in x_values],
                color="red",
                label="Regression line",
            )
            ax.set_xlabel("Deformation Distance (mm)")
            ax.set_ylabel("Strain (εyy)")
            ax.legend()
            st.pyplot(fig)

            # Display regression info with scientific formatting
            st.markdown(f"""
            **Regression Equation:**  
            εyy = {format_scientific(results["slope"], "mm⁻¹")}x + {format_scientific(results["intercept"], "")}
            
            **R² Value:** {format_scientific(results["r_squared"], "")}
            **P-value:** {format_scientific(results["p_value"], "")}
            """)

            # Display data table with scientific formatting
            df_y = pd.DataFrame(
                {
                    "Distance (mm)": [f"{x:.2f}" for x in x_values],
                    "εyy": [format_scientific(y, "") for y in y_values],
                }
            )
            st.dataframe(df_y)

        with col3:
            st.markdown("### 📈 Shear Strain (εxy)")
            y_values = [d["strain_tensor"][0, 1] for d in strain_data]
            results = regression_results["shear"]

            # Create plot
            fig, ax = plt.subplots()
            ax.scatter(x_values, y_values, color="blue", label="Data points")
            ax.plot(
                x_values,
                [results["slope"] * x + results["intercept"] for x in x_values],
                color="red",
                label="Regression line",
            )
            ax.set_xlabel("Deformation Distance (mm)")
            ax.set_ylabel("Strain (εxy)")
            ax.legend()
            st.pyplot(fig)

            # Display regression info with scientific formatting
            st.markdown(f"""
            **Regression Equation:**  
            εxy = {format_scientific(results["slope"], "mm⁻¹")}x + {format_scientific(results["intercept"], "")}
            
            **R² Value:** {format_scientific(results["r_squared"], "")}
            **P-value:** {format_scientific(results["p_value"], "")}
            """)

            # Display data table with scientific formatting
            df_xy = pd.DataFrame(
                {
                    "Distance (mm)": [f"{x:.2f}" for x in x_values],
                    "εxy": [format_scientific(y, "") for y in y_values],
                }
            )
            st.dataframe(df_xy)

        # Data export section
        st.markdown("---")  # Horizontal rule
        st.markdown("### 📥 Data Export")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📄 Raw Data")
            st.markdown("""
            Available formats:
            - JSON: File data + scale length
            - CSV: Strain components
            """)

            # Convert strain data to JSON-serializable format
            raw_data = {
                "files_data": st.session_state.files_data,
                "scale_length": scale_length,
            }
            json_str = json.dumps(raw_data, indent=2)
            st.download_button(
                "Download Raw Data (JSON)",
                json_str,
                file_name="raw_data.json",
                mime="application/json",
            )

            # Convert to CSV
            csv_data = []
            for data in strain_data:
                csv_data.append(
                    {
                        "filename": data["filename"],
                        "deformation_distance": data["deformation_distance"],
                        "strain_xx": data["strain_tensor"][0, 0],
                        "strain_yy": data["strain_tensor"][1, 1],
                        "strain_xy": data["strain_tensor"][0, 1],
                    }
                )
            df_csv = pd.DataFrame(csv_data)
            csv_str = df_csv.to_csv(index=False)
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

            # Download JSON
            json_str = json.dumps(regression_results, indent=2)
            st.download_button(
                "Download Analysis Results (JSON)",
                json_str,
                file_name="analysis_results.json",
                mime="application/json",
            )

            # Download CSV
            analysis_df = pd.DataFrame(
                [
                    {"component": "x_axis", **regression_results["x_axis"]},
                    {"component": "y_axis", **regression_results["y_axis"]},
                    {"component": "shear", **regression_results["shear"]},
                ]
            )
            csv_str = analysis_df.to_csv(index=False)
            st.download_button(
                "Download Analysis Results (CSV)",
                csv_str,
                file_name="analysis_results.csv",
                mime="text/csv",
            )

        # Important notice
        st.markdown("---")  # Horizontal rule
        st.markdown("### 🔄 Restart Analysis")
        st.info("""
        To start a new analysis:
        1. Export your data if needed
        2. Refresh your browser tab
        3. All data will be cleared and you can start fresh
        """)

# Clean up temporary file to prevent disk space issues
if os.path.exists(TEMP_IMAGE_PATH):
    os.remove(TEMP_IMAGE_PATH)
