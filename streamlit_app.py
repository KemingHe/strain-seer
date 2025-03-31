# Standard library imports
import json
import os
from typing import Dict, List, TypedDict, Optional
import uuid

# Third-party library imports
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_image_annotation import pointdet

# Local application imports
from strain_analysis_core import normalize_points_by_scale, calculate_strain_tensor
from strain_analysis_data import (
    StrainData,
    RegressionResult,
    AnalysisResults,
    analyze_strain_data,
    create_strain_plot,
    create_strain_dataframe,
    export_raw_data,
    export_analysis_results,
    format_scientific,
)
from strain_analysis_ui import (
    Point,
    FileData,
    TEMP_IMAGE_PATH,
    setup_page_config,
    initialize_session_state,
    validate_annotation,
    save_annotation,
    display_files_table,
    display_point_coordinates,
    display_analysis_results,
    display_export_section,
    cleanup_temp_files,
)

# Configure Streamlit page
setup_page_config()

# Initialize session state
initialize_session_state()

# Privacy notice
st.info(
    "🔒 Your work is saved locally in this browser tab - remember to export your data before closing"
)

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
    display_files_table(st.session_state.files_data)

    # File selection and annotation section
    st.markdown("### 🎯 Image Annotation")
    selected_filename = st.selectbox(
        "Select image to annotate",
        options=[
            data["filename"]
            for data in sorted(
                st.session_state.files_data.values(), key=lambda x: x["order"]
            )
        ],
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

        # Display point coordinates
        display_point_coordinates(file_data["points"])

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
            for data in sorted(
                st.session_state.files_data.values(), key=lambda x: x["order"]
            ):
                # Extract points
                fiducial_points = []
                scale_points = []
                for point in data["points"]:
                    if point["label"] == "Fiducial":
                        fiducial_points.append(point["point"])
                    else:
                        scale_points.append(point["point"])

                # Convert to numpy arrays and validate
                fiducial_points = np.array(fiducial_points)
                scale_points = np.array(scale_points)

                # Validate number of points
                if len(fiducial_points) != 5:
                    st.error(
                        f"File {data['filename']} must have exactly 5 fiducial points"
                    )
                    continue
                if len(scale_points) != 2:
                    st.error(
                        f"File {data['filename']} must have exactly 2 scale points"
                    )
                    continue

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

            # Analyze strain data
            st.session_state.analysis_results = analyze_strain_data(
                strain_data, scale_length
            )

        # Display analysis results
        display_analysis_results(
            st.session_state.analysis_results["strain_data"],
            st.session_state.analysis_results["regression_results"],
        )

        # Display export section
        display_export_section(
            st.session_state.files_data,
            scale_length,
            st.session_state.analysis_results["strain_data"],
            st.session_state.analysis_results["regression_results"],
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

# Clean up temporary files
cleanup_temp_files()
