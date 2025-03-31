# [Strain Seer](https://github.com/KemingHe/strain-seer) 📊

A Streamlit-based web application for 2D strain analysis using fiducial markers, designed for researchers and developers analyzing material deformation from image sequences.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Try It Now

1. **Live Demo**: Visit [strain-seer.streamlit.app](https://strain-seer.streamlit.app)
   - Note: The demo may take a few moments to wake up if it's been inactive
   - No installation required - just open and start analyzing!

2. **Demo PDF**: Check out our [example analysis](docs/demo-analysis.pdf) showing a complete use case
   - Perfect for understanding the workflow before trying it yourself
   - Includes step-by-step screenshots and results

3. **Local Installation**: See [Quick Start](#-quick-start) below for detailed setup instructions

## 🎯 Applications

Strain Seer is particularly useful for:

- **Material Science & Engineering**: Study polymer deformation, composite materials, and structural components
- **Biomechanics**: Analyze soft tissue mechanics and biological material behavior
- **Manufacturing**: Monitor material fatigue, quality control, and process optimization
- **Research & Development**: Develop custom strain formulations and multi-scale analysis methods

For a detailed understanding of 2D strain analysis and how Strain Seer implements it, check out our [Understanding 2D Strain](docs/understanding-2d-strain.md) guide.

## 🚀 Quick Start

### Option 1: Using Published Docker Image (Recommended)

```bash
# Pull and run the latest version
docker run -d -p 8501:8501 --name strain-seer ghcr.io/keminghe/strain-seer:latest

# Or pull a specific version
docker run -d -p 8501:8501 --name strain-seer ghcr.io/keminghe/strain-seer:v1.0.0
```

### Option 2: Building Docker Image Locally

```bash
# Build and run with Docker
docker build -t strain-seer .
docker run -d -p 8501:8501 --name strain-seer strain-seer
```

### Option 3: Local Installation (Advanced)

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

For detailed Docker setup and configuration, see our [Docker Design](docs/docker-design.md) documentation.

## 🛠️ Key Features

- **Interactive Point Annotation**: Easily mark fiducial points on your images
- **Real-time Strain Analysis**: Get instant feedback on material deformation
- **Multiple Strain Formulations**: Support for both small and Green-Lagrangian strain calculations
- **Data Export**: Export results in various formats for further analysis
- **Customizable Analysis**: Extend the tool with your own analysis methods

## 📚 Documentation

- [Understanding 2D Strain](docs/understanding-2d-strain.md): Comprehensive guide to strain analysis fundamentals
- [Docker Design](docs/docker-design.md): Container deployment and configuration
- [Version Management](docs/version-management.md): Project versioning and release process
- [Developer Guide](docs/developer-guide.md): Extend and customize Strain Seer's core functionality

## 🤝 Contributing

While this is primarily a tool for researchers and developers to customize for their needs, suggestions and improvements are welcome:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/KemingHe/strain-seer/blob/main/LICENSE) file for details.

## 📝 Copyright

© 2025 [Keming He](https://github.com/KemingHe). All rights reserved.
