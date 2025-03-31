# Docker Design Documentation

## 🎯 Why Docker?

Docker provides a consistent, isolated environment for running applications. For Strain Seer, this means:

- **Environment Consistency**: The same environment works on any machine (Windows, macOS, Linux)
- **Dependency Management**: All dependencies are bundled with the application
- **Deployment Simplicity**: One command to run the application
- **Version Control**: Easy to manage and distribute specific versions
- **Resource Efficiency**: Lightweight compared to full virtual machines

## 🏗️ Multi-Stage Build Design

Our Dockerfile uses a multi-stage build approach to minimize the final image size:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
# ... build stage configuration

# Stage 2: Runtime
FROM python:3.12-slim
# ... runtime stage configuration
```

This approach:

- Separates build dependencies from runtime dependencies
- Reduces final image size by excluding build tools
- Improves security by minimizing attack surface

## 🔧 Key Implementation Details

### 📦 Dependency Management

We use Poetry 2.1.2 for dependency management because:

- Matches our `pyproject.toml` requirements
- Provides deterministic builds
- Handles complex Python dependencies efficiently

The build stage installs dependencies with specific flags:

```dockerfile
RUN poetry install --without dev --no-directory --compile
```

- `--without dev`: Excludes development dependencies
- `--no-directory`: Optimizes for CI/CD environments
- `--compile`: Pre-compiles Python bytecode for better performance

### 🔒 Security Considerations

#### **Non-Root User**

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

- Prevents container from running as root
- Follows security best practices

#### **Temporary Directory**

```dockerfile
ENV TMPDIR="/tmp/app"
RUN mkdir -p /tmp/app && chown -R appuser:appuser /tmp/app
```

- Secure location for temporary files
- Proper permissions for the non-root user
- Solves Streamlit's temporary file permission issues

### 🛠️ System Dependencies

We include specific system libraries for our Python packages:

```dockerfile
RUN apt-get install -y --no-install-recommends \
    libgomp1 \
    libfreetype6 \
    libpng16-16 \
    libjpeg62-turbo
```

- `libgomp1`: Required for SciPy's parallel processing
- `libfreetype6`, `libpng16-16`, `libjpeg62-turbo`: Support for image processing and matplotlib

## 🚀 Container Lifecycle Management

### 1. Building the Image

```bash
docker build -t strain-seer .
```

- Creates a new image from the Dockerfile
- Tags it as 'strain-seer'

### 2. Running the Container

```bash
docker run -d -p 8501:8501 --name strain-seer strain-seer
```

- `-d`: Runs in detached mode (background)
- `-p 8501:8501`: Maps container port to host port
- `--name strain-seer`: Names the container for easy reference

### 3. Monitoring

```bash
docker ps | grep strain-seer
```

- Shows container status
- Displays health check information

### 4. Stopping and Cleaning Up

```bash
# Stop the container
docker stop strain-seer

# Remove the container
docker rm strain-seer

# Remove the image
docker rmi strain-seer
```

## 🧪 Health Checks

We implement health checks to monitor the application:

```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

- Ensures application is running properly
- Helps container orchestrators manage the container
- Provides early warning of issues

## 📝 Best Practices

1. **Layer Caching**:
   - Copy dependency files before application code
   - Optimize build speed and cache utilization

2. **Security**:
   - Use non-root user
   - Minimize system dependencies
   - Clean up package manager caches

3. **Performance**:
   - Multi-stage builds
   - Pre-compiled Python bytecode
   - Optimized dependency installation

4. **Maintainability**:
   - Clear stage separation
   - Well-documented environment variables
   - Consistent naming conventions

## 🔄 Future Considerations

1. **Versioning**:
   - Consider using specific version tags
   - Implement automated version bumping

2. **CI/CD Integration**:
   - Add automated testing in container
   - Implement automated builds and pushes

3. **Monitoring**:
   - Add logging configuration
   - Consider metrics collection

4. **Security**:
   - Regular dependency updates
   - Security scanning integration
