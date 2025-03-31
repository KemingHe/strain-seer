# Version Management Workflow

This document outlines the standard workflow for version management in the Strain Seer project. Following these guidelines ensures consistent and professional version control practices.

## 📊 Version Numbering

We follow [Semantic Versioning](https://semver.org/) (SemVer) for our version numbers in the format `x.y.z`:

- **Major Version (x)**: Breaking changes that are not backward compatible
  - Example: `1.0.0` → `2.0.0`
  - Use when: Removing features, changing API contracts
  - Conventional commit: `feat!: remove deprecated API endpoints`

- **Minor Version (y)**: New features that maintain backward compatibility
  - Example: `1.0.0` → `1.1.0`
  - Use when: Adding new features, enhancing existing functionality
  - Conventional commit: `feat: add new visualization component`

- **Patch Version (z)**: Bug fixes and minor improvements
  - Example: `1.0.0` → `1.0.1`
  - Use when: Fixing bugs, improving performance
  - Conventional commit: `fix: resolve memory leak in data processing`

## 🔄 Version Bump Process

1. **Update Version Number**

   ```bash
   poetry version <major|minor|patch>
   ```

   This will automatically update the version in `pyproject.toml`.

2. **Commit Changes**
   - Use conventional commit messages following the format:

     ```text
     type(scope): description
     ```

   - Types:
     - `feat`: New features
     - `fix`: Bug fixes
     - `docs`: Documentation changes
     - `style`: Code style changes
     - `refactor`: Code refactoring
     - `perf`: Performance improvements
     - `test`: Adding or modifying tests
     - `chore`: Maintenance tasks

   Examples:

   ```text
   feat(api): add new endpoint for strain analysis
   fix(ui): resolve responsive layout issues
   docs(readme): update installation instructions
   ```

3. **Create Git Tag**

   ```bash
   git tag -s v$(poetry version --short) -m "v$(poetry version --short) - Summary of changes"
   ```

   Example:

   ```bash
   git tag -s v1.2.0 -m "v1.2.0 - Add new visualization features and performance improvements"
   ```

4. **Push Changes**

   ```bash
   git push origin main
   git push origin v$(poetry version --short)
   ```

5. **Create GitHub Release**
   - Go to GitHub repository → Releases → Create new release
   - Select the newly created tag
   - Add detailed release notes
   - Publish release

## 🤖 Automated Processes

Upon release creation:

- GitHub Actions automatically builds the Docker image
- Image is published to GitHub Container Registry (ghcr.io)
- Release notes are generated from conventional commits

## 🔒 Access Control

> [!WARNING]
>
> This project uses a simplified version management approach suitable for small teams.

Larger projects might want to consider:

- Branch protection rules requiring pull requests
- Automated version bumping through CI/CD
- Release branch strategy
- Automated changelog generation

Only repository administrators with bypass permissions can:

- Directly push to main branch
- Create and push tags
- Create releases

All other team members must:

1. Create feature branches
2. Submit pull requests
3. Get code review approval
4. Merge through pull request

## 💡 Best Practices

1. **Version Bumping**
   - Always bump version before creating a release
   - Use appropriate version level based on changes
   - Document breaking changes clearly

2. **Commit Messages**
   - Be descriptive and clear
   - Reference issue numbers when applicable
   - Keep commits focused and atomic

3. **Release Notes**
   - Include all significant changes
   - Highlight breaking changes
   - Provide migration guides if needed

4. **Tag Management**
   - Always sign tags for security
   - Use meaningful tag messages
   - Keep tags in sync with releases
