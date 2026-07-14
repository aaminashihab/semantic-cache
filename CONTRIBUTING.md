# Contributing to Semantic Cache

Thank you for your interest in contributing to the Semantic Cache project! We welcome contributions from the community. This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs if possible**
- **Include your environment details** (OS, Python version, package versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Follow the Python style guide (PEP 8)
- Include appropriate test cases
- Update documentation as needed
- Add an entry to the [CHANGELOG.md](CHANGELOG.md) file
- Reference any related issues in your PR description
- Ensure all CI/CD checks pass

#### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/semantic-cache.git
   cd semantic-cache
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

#### Running Tests

```bash
pytest tests/
```

#### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **isort** for import sorting

Run these tools before submitting a PR:

```bash
black .
isort .
flake8 .
```

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit with clear commit messages
3. Push to your fork
4. Create a Pull Request with a clear description of the changes
5. Link any related issues using `Closes #issue-number`
6. Ensure the PR description follows the template
7. Wait for code review and CI checks to pass
8. Address any feedback from reviewers

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Documentation

- Update README.md if you add or change features
- Add docstrings to all functions and classes
- Keep documentation clear and up-to-date
- Include examples where appropriate

## License

By contributing to Semantic Cache, you agree that your contributions will be licensed under its MIT License.

## Questions?

Feel free to open an issue for any questions or reach out to the maintainers.

Thank you for contributing! 🎉
