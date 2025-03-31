# Strain Seer 📊

A Streamlit-based web application for 2D strain analysis using fiducial markers. Built for researchers and developers who need to analyze material deformation from image sequences.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚠️ Requirements

- Python: `3.12.5`
- Poetry: `>2.0`
- See [pyproject.toml](https://github.com/KemingHe/strain-seer/blob/main/pyproject.toml) for detailed dependency specifications

## 🚀 Quick Start

```bash
# Install pyenv (recommended for Python version management)
curl https://pyenv.run | bash

# Install Python 3.12.5 using pyenv
pyenv install 3.12.5
pyenv global 3.12.5

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup
git clone https://github.com/KemingHe/strain-seer.git
cd strain-seer

# Create and activate virtual environment
poetry env use python3.12.5
poetry env activate
eval "$(poetry env activate)"

# Install dependencies
poetry install

# Run the app
streamlit run streamlit_app.py
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=strain_seer
```

## 🛠️ Core Components

### 1. Strain Analysis Engine ([strain_analysis.py](https://github.com/KemingHe/strain-seer/blob/main/strain_analysis.py))

- Implements 2D strain tensor calculation
- Supports both small and Green-Lagrangian strain formulations
- Handles point normalization and scale calibration

### 2. Web Interface ([streamlit_app.py](https://github.com/KemingHe/strain-seer/blob/main/streamlit_app.py))

- Interactive point annotation
- Real-time strain visualization
- Data export in multiple formats

## 🔧 Customization Guide

### 1. Strain Analysis Modifications

```python
# strain_analysis.py
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

### 2. UI Enhancements

```python
# streamlit_app.py
# Add new visualization types
def plot_strain_heatmap(strain_tensor: np.ndarray):
    # Your custom visualization code
    pass

# Extend data export formats
def export_to_custom_format(data: Dict):
    # Your custom export logic
    pass
```

### 3. Data Processing Pipeline

- Modify point validation logic in `validate_annotation()`
- Add custom data preprocessing steps
- Implement new data export formats

## 🎯 Research Applications

Strain Seer enables researchers to analyze material deformation across diverse fields:

- **Material Science & Engineering**: Study polymer deformation, composite materials, and structural components
- **Biomechanics**: Analyze soft tissue mechanics and biological material behavior
- **Manufacturing**: Monitor material fatigue, quality control, and process optimization
- **Research & Development**: Develop custom strain formulations and multi-scale analysis methods

The tool's accessibility and extensibility make it ideal for both rapid prototyping and production research workflows.

## 📦 Dependencies

Key dependencies with version constraints:

```text
streamlit>=1.44.0,<2.0.0
streamlit-image-annotation>=0.5.0,<0.6.0
matplotlib>=3.10.1,<4.0.0
scipy>=1.15.2,<2.0.0
```

See [pyproject.toml](https://github.com/KemingHe/strain-seer/blob/main/pyproject.toml) for complete dependency list.

## 🔍 Technical Details

### Strain Tensor Components

- εxx: Normal strain in x-direction
- εyy: Normal strain in y-direction
- εxy: Shear strain

### Point Configuration

```text
0 ------- 1
|  \   /  |
|    4    |
|  /   \  |
3 ------- 2
```

### Data Flow

1. Image upload → Point annotation
2. Scale calibration → Point normalization
3. Strain calculation → Visualization
4. Data export → Analysis

## 🤝 Contributing

While this is primarily a tool for researchers and developers to customize for their needs, suggestions and improvements are welcome:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Setup

```bash
# Install development dependencies
poetry install --with test

# Run tests before committing
pytest

# Install ruff globally for linting (recommended)
pipx install ruff

# Lint code
ruff check .
ruff format .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/KemingHe/strain-seer/blob/main/LICENSE) file for details.

## 🔗 Links

- [Live Demo](https://strain-seer.streamlit.app)
- [GitHub Repository](https://github.com/KemingHe/strain-seer)
- [Issue Tracker](https://github.com/KemingHe/strain-seer/issues)

## 📝 Copyright

© 2025 [Keming He](https://github.com/KemingHe). All rights reserved.
