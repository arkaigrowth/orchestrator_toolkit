# Contributing to Orchestrator Toolkit

First off, thank you for considering contributing to Orchestrator Toolkit! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

1. **Use a clear and descriptive title**
2. **Describe the exact steps to reproduce the problem**
3. **Provide specific examples**
4. **Describe the behavior you observed and what you expected**
5. **Include system information:**
   - OS and version
   - Python version
   - Orchestrator Toolkit version
   - Relevant environment variables

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

1. **Use a clear and descriptive title**
2. **Provide a detailed description of the suggested enhancement**
3. **Provide specific examples to demonstrate the enhancement**
4. **Describe the current behavior and explain the expected behavior**
5. **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/orchestrator_toolkit_1.0.git
cd orchestrator_toolkit_1.0

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
pip install pytest black mypy ruff  # Development tools

# Create a branch
git checkout -b feature/your-feature-name
```

## Development Guidelines

### Python Style Guide

We follow PEP 8 with these specifics:

- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped as standard library, third-party, local
- **Type hints**: Use where beneficial for clarity

### Code Quality Tools

```bash
# Format code with Black
black src/

# Check types with mypy
mypy src/

# Lint with ruff
ruff check src/

# Run tests
pytest tests/
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only changes
- `style:` Code style changes (formatting, semicolons, etc)
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `test:` Adding or correcting tests
- `chore:` Changes to build process or auxiliary tools

Examples:
```
feat: add support for custom template directory
fix: correct ID generation for edge case with 10000+ tasks
docs: update README with Windows installation instructions
```

### Testing

- Write tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage for new code
- Test edge cases and error conditions

Example test structure:
```python
def test_task_creation():
    """Test that tasks are created with correct format."""
    # Arrange
    title = "Test task"
    owner = "Test owner"

    # Act
    result = create_task(title, owner)

    # Assert
    assert result.exists()
    assert "Test task" in result.read_text()
```

### Documentation

- Update README.md if changing user-facing functionality
- Add docstrings to all public functions
- Include type hints where helpful
- Update examples/ if adding new features

Docstring format:
```python
def create_task(title: str, owner: str = "unknown") -> Path:
    """Create a new task file in the artifact directory.

    Args:
        title: The task title/description
        owner: The person or team responsible

    Returns:
        Path to the created task file

    Raises:
        ValueError: If title is empty
    """
```

## Project Structure

```
src/orchestrator_toolkit/
├── settings.py          # Configuration management
├── utils.py            # Utility functions
├── id_alloc.py         # ID generation logic
├── orchestrator.py     # Core orchestration
├── cli.py             # CLI entry points
└── scripts/           # Command implementations
    ├── task_new.py
    └── plan_new.py
```

### Key Design Principles

1. **Single Source of Truth**: Settings managed through `OrchSettings.load()`
2. **Directory-Based IDs**: No counter files, scan directory for next ID
3. **Safe Migration**: Never lose user data during migrations
4. **Cross-Platform**: Must work on Windows, macOS, and Linux
5. **Zero Configuration**: Sensible defaults with environment overrides

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag -a v1.0.1 -m "Release version 1.0.1"`
4. Push tag: `git push origin v1.0.1`
5. Create GitHub release from tag

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Clarification on contributing guidelines
- Discussion about potential features

## Recognition

Contributors will be recognized in:
- The project README
- Release notes for their contributions
- The AUTHORS file (for significant contributions)

Thank you for helping make Orchestrator Toolkit better! 🎯