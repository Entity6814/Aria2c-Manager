# Contributing to Aria2c Manager

Thank you for your interest in contributing to Aria2c Manager! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8+
- aria2c installed and accessible via PATH
- Git installed
- Basic knowledge of Python, JavaScript, and PyQt6

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/Entity6814/Aria2c-Manager.git
   cd Aria2c-Manager
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up development environment**
   ```bash
   # Start aria2c daemon for testing
   python start_aria2.py
   
   # In another terminal, start GUI
   python app.pyw
   ```

## Development Workflow

### Branch Strategy

- **main**: Stable production code
- **develop**: Development branch for new features
- **feature/***: Individual feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Urgent production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Code style**: Follow existing code conventions
2. **Comments**: Add clear comments for complex logic
3. **Testing**: Test your changes thoroughly
4. **Documentation**: Update relevant documentation

### Commit Guidelines

**Commit message format:**
```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(extension): add custom download directory configuration

- Added options.html for user settings
- Implemented chrome.storage for persistence
- Updated background.js to use configured directory

Closes #123
```

```
fix(gui): prevent download selection loss during refresh

- Changed from table-based to widget-based layout
- Added individual download cards with inline controls
- Fixed state management for download widgets

Fixes #456
```

### Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to GitHub and create PR
   - Fill in PR template
   - Link related issues
   - Request review from maintainers

4. **Address feedback**
   - Make requested changes
   - Push updates to your branch
   - Respond to reviewer comments

## Code Style Guidelines

### Python

- **PEP 8 compliance**: Follow PEP 8 style guide
- **Line length**: Maximum 100 characters
- **Imports**: Group imports (standard library, third-party, local)
- **Naming**: 
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

**Example:**
```python
import sys
import os
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow

class DownloadManager:
    def __init__(self):
        self.download_queue = []
        self.max_connections = 16
    
    def add_download(self, url, options=None):
        """Add a new download to the queue."""
        # Implementation here
        pass
```

### JavaScript

- **ES6+ syntax**: Use modern JavaScript features
- **Consistent indentation**: 2 spaces
- **Semicolons**: Use semicolons consistently
- **String quotes**: Prefer single quotes, use double for strings with single quotes

**Example:**
```javascript
async function getDownloadDirectory() {
  try {
    const result = await new Promise((resolve) => {
      chrome.storage.local.get(['downloadDir'], (data) => {
        resolve(data);
      });
    });
    return result.downloadDir || "";
  } catch (error) {
    console.log("Error:", error);
    return "";
  }
}
```

### HTML/CSS

- **Semantic HTML**: Use appropriate HTML5 elements
- **CSS naming**: BEM methodology preferred
- **Responsive design**: Mobile-friendly styles

## Testing

### Manual Testing Checklist

- [ ] aria2c daemon starts correctly
- [ ] GUI connects to RPC server
- [ ] Browser extension loads without errors
- [ ] Download interception works
- [ ] Manual URL addition works
- [ ] Pause/resume functionality works
- [ ] Cancel/remove functionality works
- [ ] System tray integration works
- [ ] Notifications appear correctly
- [ ] Download location is correct

### Testing Different Scenarios

1. **Happy path**: Normal download flow
2. **Error cases**: Network failures, aria2c not running
3. **Edge cases**: Large files, special characters in filenames
4. **Compatibility**: Different browsers, different OS

## Documentation

### When to Update Documentation

- Adding new features
- Changing configuration options
- Modifying installation process
- Updating dependencies
- Changing API interfaces

### Documentation Files

- **README.md**: Update for user-facing changes
- **INSTALL.md**: Update for installation changes
- **CONTRIBUTING.md**: Update for development process changes
- **Code comments**: Update for code logic changes

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues**: Check if your issue already exists
2. **Check documentation**: Review README and INSTALL guides
3. **Test latest version**: Ensure you're using the latest version

### Issue Template

```markdown
## Description
[What is the issue?]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

## Expected Behavior
[What should happen?]

## Actual Behavior
[What actually happens?]

## Environment
- OS: [Windows/Linux/Mac + version]
- Python version: [e.g., 3.9.7]
- aria2c version: [e.g., 1.37.0]
- Browser: [Chrome/Edge + version]

## Screenshots
[If applicable]

## Additional Context
[Any other relevant information]
```

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
[What feature would you like?]

## Use Case
[Why do you need this feature?]

## Proposed Solution
[How should this feature work?]

## Alternatives Considered
[What alternatives have you considered?]

## Additional Context
[Any other relevant information]
```

## Release Process

### Versioning

We follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number updated
- [ ] Tagged in Git
- [ ] Release created on GitHub

## Communication

### Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Pull Requests**: For code contributions

### Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation for major features

## Questions?

If you have questions about contributing:
- Check existing issues and discussions
- Review this contributing guide
- Ask in GitHub Discussions
- Open an issue with the "question" label

Thank you for contributing to Aria2c Manager!
