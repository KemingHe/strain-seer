# [👁️ Strain Seer](https://github.com/KemingHe/strain-seer)

<div align="center">

[![A Streamlit app for 2D strain analysis using fiducial markers, designed for analyzing material deformation from image sequences](https://socialify.git.ci/KemingHe/strain-seer/image?description=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FKemingHe%2Fstrain-seer%2Fmain%2Fdocs%2Fstrain-seer-icon.png&name=1&owner=1&theme=Dark)](https://github.com/KemingHe/strain-seer)

[![Build Status](https://img.shields.io/github/actions/workflow/status/KemingHe/strain-seer/build-test.yaml)](https://github.com/KemingHe/strain-seer/actions/workflows/build-test.yaml) &nbsp; [![Codcov Status](https://codecov.io/gh/KemingHe/strain-seer/graph/badge.svg?token=BCJ4AJUW1I)](https://codecov.io/gh/KemingHe/strain-seer) &nbsp; [![GitHub License](https://img.shields.io/github/license/KemingHe/strain-seer)](https://github.com/KemingHe/strain-seer/blob/main/LICENSE) &nbsp; [![GitHub Release](https://img.shields.io/github/v/release/KemingHe/strain-seer)](https://github.com/KemingHe/strain-seer/releases)

</div>

## 🚀 Try It Now

1. **Live Demo**: Visit [strain-seer.streamlit.app](https://strain-seer.streamlit.app)
   - Note: The demo may take a few moments to wake up if it's been inactive
   - No installation required - just open and start analyzing!

2. **Demo PDF**: Check out our [example analysis](docs/strain-seer-demo.pdf) showing a complete use case
   - Perfect for understanding the workflow before trying it yourself
   - Includes step-by-step screenshots and results
   - Sample data files are available in the docs directory, including [raw data](docs/strain-seer-demo-raw-data.csv) and [analysis results](docs/strain-seer-demo-analysis-result.csv)

3. **Local Installation**: See [Quick Start](#-quick-start) below for detailed setup instructions

## 🎯 Applications

Strain Seer is particularly useful for:

- **Material Science & Engineering**: Study polymer deformation, composite materials, and structural components
- **Biomechanics**: Analyze soft tissue mechanics and biological material behavior
- **Manufacturing**: Monitor material fatigue, quality control, and process optimization
- **Research & Development**: Develop custom strain formulations and multi-scale analysis methods

For a detailed understanding of 2D strain analysis and how Strain Seer implements it, check out our [Understanding 2D Strain](docs/understanding-2d-strain.md) guide, which includes point labeling conventions, strain tensor explanations with visual examples, and step-by-step calculation processes.

## 🚀 Quick Start

### Option 1: Using Published Docker Image (Recommended)

```bash
# Pull and run the latest version
docker run -d -p 8501:8501 --name strain-seer ghcr.io/keminghe/strain-seer:latest

# Or pull a specific version
docker run -d -p 8501:8501 --name strain-seer ghcr.io/keminghe/strain-seer:v1.0.0
```

For detailed Docker setup and configuration, see our [Docker Design](docs/docker-design.md) documentation, which covers multi-stage builds, dependency management, security considerations, and container lifecycle management.

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

## 🛠️ Key Features

- **Interactive Point Annotation**: Easily mark fiducial points on your images
- **Real-time Strain Analysis**: Get instant feedback on material deformation
- **Multiple Strain Formulations**: Support for both small and Green-Lagrangian strain calculations
- **Data Export**: Export results in various formats for further analysis
- **Customizable Analysis**: Extend the tool with your own analysis methods

## 📚 Documentation

Our documentation is structured to help you understand, use, and extend Strain Seer:

- [Understanding 2D Strain](docs/understanding-2d-strain.md): A comprehensive guide to strain analysis fundamentals with clear labeling conventions, visual examples, and numerical calculation walkthroughs
- [Developer Guide](docs/developer-guide.md): Detailed documentation for extending and customizing Strain Seer's core functionality, including core components, customization guides, and dependency management
- [Testing Strategy](tests/README.md): Our approach to testing, focusing on core strain analysis algorithms and data processing while maintaining a pragmatic balance with UI testing
- [Version Management](docs/version-management.md): Guidelines for semantic versioning, version bumping process, conventional commit messages, and best practices for release management
- [Docker Design](docs/docker-design.md): Detailed information about container deployment, multi-stage builds, security considerations, and container lifecycle management

The project also includes automated CI/CD workflows in the `.github/workflows` directory:

- [**Unit Tests**](.github/workflows/unit-test.yaml): Ensures code quality with pytest and coverage reporting
- [**Build Tests**](.github/workflows/built-test.yaml): Validates Docker builds across multiple platforms (AMD64, ARM64)
- [**Docker Publish**](.github/workflows/docker-publish.yaml): Automatically publishes versioned images to GitHub Container Registry when releases are created

> [!NOTE]
>
> The `docs/hammer-challenge` directory contains materials specific to the Make OHI/O 2025 competition and can be safely deleted if you're forking this repository or using it as a template for your own project.

## 🤝 Contributing

While this is primarily a tool for researchers and developers to customize for their needs, suggestions and improvements are welcome:

1. Fork the repository
2. Create your feature branch
3. Commit your changes (following our [version management guidelines](docs/version-management.md))
4. Push to the branch
5. Create a Pull Request

Please follow our [testing strategy](tests/README.md) to ensure your changes maintain the project's quality standards. We prioritize testing core strain analysis algorithms and data processing functions, while taking a pragmatic approach to UI testing.

All contributions automatically trigger our CI workflows to ensure code quality. For detailed information about the CI/CD pipeline, see the [GitHub Actions workflows documentation](.github/workflows/README.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/KemingHe/strain-seer/blob/main/LICENSE) file for details.

## 📝 Copyright

© 2025 [Keming He](https://github.com/KemingHe). All rights reserved.
