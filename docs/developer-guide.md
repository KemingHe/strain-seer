# Developer Guide

This guide explains how to extend and customize Strain Seer's core functionality. It's intended for researchers and developers who want to modify the tool for their specific needs.

## 🏗️ Core Components

### 1. Strain Analysis Core ([strain_analysis_core.py](https://github.com/KemingHe/strain-seer/blob/main/strain_analysis_core.py))

- Implements 2D strain tensor calculation
- Supports both small and Green-Lagrangian strain formulations
- Handles point normalization and scale calibration

### 2. Strain Analysis Data ([strain_analysis_data.py](https://github.com/KemingHe/strain-seer/blob/main/strain_analysis_data.py))

- Data analysis and regression
- Visualization and plotting
- Data export in multiple formats

### 3. Strain Analysis UI ([strain_analysis_ui.py](https://github.com/KemingHe/strain-seer/blob/main/strain_analysis_ui.py))

- Interactive point annotation
- Real-time strain visualization
- Data export in multiple formats
- Session state management
- File handling and cleanup

### 4. Web Interface ([streamlit_app.py](https://github.com/KemingHe/strain-seer/blob/main/streamlit_app.py))

- Main application flow
- User interface layout
- Component orchestration

## 🔧 Customization Guide

### 1. Strain Analysis Core Modifications

The core strain calculation can be customized by modifying the `calculate_strain_tensor` function:

```python
# strain_analysis_core.py
def calculate_strain_tensor(
    original_points: np.ndarray,
    deformed_points: np.ndarray,
    strain_type: Literal["small", "green_lagrangian"] = "small",
    center_index: int = 4
) -> np.ndarray:
```

- Add new strain formulations by extending `strain_type`
- Modify point ordering by adjusting `center_index`
- Implement custom normalization methods

### 2. Data Analysis Customization

The `strain_analysis_data.py` module is designed to be easily extensible for researchers to add their own analysis methods.

#### A. Adding New Analysis Methods

```python
# strain_analysis_data.py

def analyze_strain_data(
    strain_data: List[StrainData], 
    scale_length: float,
    analysis_method: str = "linear_regression"  # Add your method here
) -> AnalysisResults:
    """Analyze strain data using specified method."""
    if analysis_method == "linear_regression":
        return analyze_linear_regression(strain_data, scale_length)
    elif analysis_method == "your_method":
        return analyze_your_method(strain_data, scale_length)
    else:
        raise ValueError(f"Unknown analysis method: {analysis_method}")

def analyze_your_method(strain_data: List[StrainData], scale_length: float) -> AnalysisResults:
    """Your custom analysis method."""
    # Your analysis code here
    pass
```

#### B. Custom Visualization

```python
# strain_analysis_data.py

def create_strain_plot(
    x_values: List[float],
    y_values: List[float],
    results: RegressionResult,
    title: str,
    ylabel: str,
    plot_type: str = "scatter"  # Add your plot type
) -> plt.Figure:
    """Create a plot for strain data."""
    if plot_type == "scatter":
        return create_scatter_plot(x_values, y_values, results, title, ylabel)
    elif plot_type == "your_plot":
        return create_your_plot(x_values, y_values, results, title, ylabel)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

def create_your_plot(x_values: List[float], y_values: List[float], ...) -> plt.Figure:
    """Your custom visualization."""
    # Your plotting code here
    pass
```

#### C. Custom Data Export

```python
# strain_analysis_data.py

def export_analysis_results(
    regression_results: Dict[str, RegressionResult],
    format: str = "json"  # Add your format
) -> tuple[str, str]:
    """Export analysis results in specified format."""
    if format == "json":
        return export_json(regression_results)
    elif format == "your_format":
        return export_your_format(regression_results)
    else:
        raise ValueError(f"Unknown format: {format}")

def export_your_format(regression_results: Dict[str, RegressionResult]) -> tuple[str, str]:
    """Your custom export format."""
    # Your export code here
    pass
```

### 3. UI Enhancements

The `strain_analysis_ui.py` module provides a clean interface for customizing the application's user interface.

#### A. Adding New Visualization Types

```python
# strain_analysis_ui.py

def display_analysis_results(
    strain_data: List[StrainData],
    regression_results: Dict[str, RegressionResult],
    visualization_type: str = "default"  # Add your visualization type
):
    """Display analysis results with custom visualization."""
    if visualization_type == "default":
        display_default_visualization(strain_data, regression_results)
    elif visualization_type == "heatmap":
        display_strain_heatmap(strain_data, regression_results)
    elif visualization_type == "your_visualization":
        display_your_visualization(strain_data, regression_results)
    else:
        raise ValueError(f"Unknown visualization type: {visualization_type}")

def display_strain_heatmap(strain_data: List[StrainData], regression_results: Dict[str, RegressionResult]):
    """Display strain data as a heatmap."""
    # Your heatmap visualization code here
    pass
```

#### B. Custom Export Interface

```python
# strain_analysis_ui.py

def display_export_section(
    files_data: Dict[str, FileData],
    scale_length: float,
    strain_data: List[StrainData],
    regression_results: Dict[str, RegressionResult],
    export_format: str = "default"  # Add your export format
):
    """Display export section with custom format."""
    if export_format == "default":
        display_default_export(files_data, scale_length, strain_data, regression_results)
    elif export_format == "custom":
        display_custom_export(files_data, scale_length, strain_data, regression_results)
    else:
        raise ValueError(f"Unknown export format: {export_format}")

def display_custom_export(
    files_data: Dict[str, FileData],
    scale_length: float,
    strain_data: List[StrainData],
    regression_results: Dict[str, RegressionResult]
):
    """Display custom export interface."""
    # Your custom export interface code here
    pass
```

## 🧪 Testing

When adding new features or customizations, make sure to:

1. Write unit tests for new functions
2. Add integration tests for UI components
3. Test with various input data types
4. Verify backward compatibility

```bash
# Run tests
pytest

# Run with coverage
pytest --cov
```

## 📦 Dependencies

When adding new features, you may need to add dependencies to `pyproject.toml`. Key dependencies include:

```text
streamlit>=1.44.0,<2.0.0
streamlit-image-annotation>=0.5.0,<0.6.0
matplotlib>=3.10.1,<4.0.0
scipy>=1.15.2,<2.0.0
```

See [pyproject.toml](https://github.com/KemingHe/strain-seer/blob/main/pyproject.toml) for complete dependency list.
