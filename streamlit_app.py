import streamlit as st
from streamlit_image_annotation import pointdet
from PIL import Image
import io
import os
import pandas as pd
from pathlib import Path

# Set page config with favicon
st.set_page_config(
    page_title="Point Annotation Tool",
    page_icon="📍",
    layout="wide"
)

# Initialize session state for files data
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# Title and description
st.title("Point Annotation Tool")
st.markdown("""
This tool allows you to annotate points on multiple images:
- **Click**: Add/Remove points
- **Fiducial Points** (Red): Used for reference points (5 required)
- **Scale Points** (Green): Used for scale measurement (2 required)

### Instructions:
1. Upload your image files
2. Select a file from the list below
3. Annotate the required points:
   - 5 Fiducial points (red)
   - 2 Scale points (green)
4. The status will update automatically
""")

# Define label list with colors
label_list = ['Fiducial', 'Scale']

def validate_annotation(points):
    """Validate if annotation meets requirements."""
    if not points:
        return False, "Missing"
    
    fiducial_count = sum(1 for p in points if p['label'] == 'Fiducial')
    scale_count = sum(1 for p in points if p['label'] == 'Scale')
    
    if fiducial_count != 5 or scale_count != 2:
        return False, "Incomplete"
    return True, "Complete"

def save_annotation(file_name, points):
    """Save annotation data to session state."""
    st.session_state.files_data[file_name] = {
        'points': points or [],  # Ensure points is never None
        'status': validate_annotation(points or [])
    }

# File uploader
uploaded_files = st.file_uploader(
    "Choose image files", 
    type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
    accept_multiple_files=True
)

# Save uploaded files and initialize their data
for uploaded_file in uploaded_files:
    if uploaded_file.name not in st.session_state.files_data:
        save_annotation(uploaded_file.name, [])

# Display files table with status
if st.session_state.files_data:
    files_df = pd.DataFrame([
        {
            'File': name,
            'Status': data['status'][1],
            'Fiducial Points': sum(1 for p in data.get('points', []) if p.get('label') == 'Fiducial'),
            'Scale Points': sum(1 for p in data.get('points', []) if p.get('label') == 'Scale')
        }
        for name, data in st.session_state.files_data.items()
    ])
    
    # Color coding for status
    def color_status(val):
        if val == 'Complete':
            return 'color: green'
        elif val == 'Incomplete':
            return 'color: orange'
        return 'color: red'
    
    st.markdown("### Files Status")
    st.dataframe(
        files_df.style.applymap(color_status, subset=['Status']),
        hide_index=True
    )
    
    # File selection
    st.markdown("### Select File to Annotate")
    selected_file = st.selectbox(
        "Choose a file to annotate",
        options=list(st.session_state.files_data.keys())
    )
    
    if selected_file:
        file_data = st.session_state.files_data[selected_file]
        
        # Save the image temporarily
        temp_path = "temp_image.jpg"
        for uploaded_file in uploaded_files:
            if uploaded_file.name == selected_file:
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                break
        
        # Point detection annotation
        points = pointdet(
            temp_path,
            label_list=label_list,
            points=[[p['point'][0], p['point'][1]] for p in file_data['points']],
            labels=[0 if p['label'] == 'Fiducial' else 1 for p in file_data['points']],
            height=512,
            width=512,
            point_width=3,
            use_space=True
        )
        
        # Save new annotation
        if points:  # Only update if we got new points
            save_annotation(selected_file, points)
        
        # Display current annotation table
        if file_data['points']:  # Use file_data instead of points
            df_data = []
            for i, point in enumerate(file_data['points']):
                df_data.append({
                    'Type': point['label'],
                    'Order': i + 1,
                    'X': f"{point['point'][0]:.1f}",
                    'Y': f"{point['point'][1]:.1f}"
                })
            
            df = pd.DataFrame(df_data)
            
            st.markdown("### Current Annotation")
            st.dataframe(
                df.style.applymap(
                    lambda x: 'color: red' if x == 'Fiducial' else 'color: green',
                    subset=['Type']
                ),
                hide_index=True
            )
    
    # Debug section
    st.markdown("### Debug Information")
    st.markdown("All files data:")
    st.json(st.session_state.files_data)

# Clean up temporary file
if os.path.exists("temp_image.jpg"):
    os.remove("temp_image.jpg")
