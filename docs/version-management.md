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

### 👥 For Contributors

1. **Include Version Bump in Feature Branch**
   - When creating a feature/fix branch, include version bump if needed
   - Use appropriate version level based on changes:

     ```shell
     poetry version <major|minor|patch>
     ```

   - Commit the version bump with conventional commit message:

     ```text
     chore(release): bump version to vX.Y.Z
     ```

2. **Create Pull Request**
   - Push your branch
   - Create a pull request for review
   - Include version bump details in the PR description if applicable
   - Follow regular PR process

### 👑 For Repository Owners/Administrators

1. **Review and Merge**
   - Review the pull request including version changes
   - Ensure version bump is appropriate for the changes
   - Merge the pull request

2. **Create Git Tag**

   ```shell
   git tag -s v$(poetry version --short) -m "v$(poetry version --short) - Summary of changes"
   ```

   Example:

   ```shell
   git tag -s v1.2.0 -m "v1.2.0 - Add new visualization features and performance improvements"
   ```

3. **Push Changes and Tags**

   ```shell
   git push origin v$(poetry version --short)
   ```

4. **Create GitHub Release**
   - Go to GitHub repository → Releases → Create new release
   - Select the newly created tag
   - Add detailed release notes
   - Publish release

## 🤖 Automated Processes

Upon release creation:

- GitHub Actions automatically builds the Docker image
- Image is published to GitHub Container Registry (ghcr.io)

## 🔒 Access Control and Responsibilities

### 👑 Repository Owner/Administrators

Repository owners maintain project integrity and security:

- **Version Control**: Create tags and releases to ensure stable release points
- **Code Quality**: Review and merge PRs to maintain code standards
- **Security**: Manage access and sensitive configurations

### 👥 Contributors

Contributors follow these guidelines to maintain project quality:

- **Branch Workflow**: Create feature branches with your username

  ```text
  feature/add-new-visualization/KemingHe
  test/improved-core-coverage/KemingHe
  fix/memory-leak/KemingHe
  ```

- **PR Process**: Submit PRs for all changes and address review feedback
- **Version Control**: Include version bumps in feature PRs when needed

## 💡 Best Practices

1. **Version Management**
   - Bump versions based on impact: major (breaking), minor (features), patch (fixes)
   - Document breaking changes to help users migrate smoothly

   ```markdown
   # Breaking Changes in v2.0.0
   - Removed deprecated API endpoints
   - New authentication flow required
   Migration guide: [link]
   ```

2. **Code Quality**
   - Write clear commit messages that explain the "why" not just the "what"

   ```text
   # Good
   feat(auth): implement OAuth2 for better security
   # Bad
   feat(auth): add OAuth2
   ```

   - Keep changes focused and atomic for easier review and rollback

3. **Release Process**
   - Sign tags for security and traceability
   - Write meaningful release notes that highlight user-impacting changes

   ```markdown
   # Release v1.2.0
   ## Features
   - New visualization component for strain analysis
   - Improved performance in data processing
   ## Breaking Changes
   - None
   ```
