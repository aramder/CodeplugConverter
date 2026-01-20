# Contributing to PMR-171 CPS

Thank you for your interest in contributing to PMR-171 CPS! This project welcomes contributions from the community.

## 🤖 AI-Assisted Development

This project was developed entirely with AI assistance. We encourage contributors to use AI tools in their workflow:

1. **Describe** the feature or fix in natural language
2. **Use AI** to help implement and test
3. **Review** the generated code for correctness
4. **Submit** a well-documented PR

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- (Optional) PMR-171 radio for hardware testing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/aramder/PMR_171.git
cd PMR_171

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pmr_171_cps

# Run specific test file
pytest tests/test_pmr171_format_validation.py -v
```

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Suggesting Features

1. Check TODO.md for planned features
2. Open an issue with the feature request template
3. Describe the use case and benefit

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, descriptive commits
4. **Add tests** for new functionality
5. **Run tests** to ensure nothing is broken
6. **Update documentation** if needed
7. **Submit a Pull Request**

### Pull Request Guidelines

- Follow existing code style
- Include tests for new features
- Update documentation as needed
- Keep PRs focused on a single change
- Reference related issues

## Code Style

- Use meaningful variable names
- Add docstrings to functions and classes
- Follow PEP 8 guidelines
- Use type hints where appropriate

## Project Structure

```
pmr_171_cps/
├── gui/          # GUI components (tkinter)
├── radio/        # UART communication
├── parsers/      # File format parsers
├── writers/      # Output writers
└── utils/        # Utility functions
```

## Testing with Hardware

If you have a PMR-171 radio:

1. **Always backup** your radio before testing
2. Use `--dry-run` flag for read-only tests
3. Test on non-critical channels first
4. Document hardware testing results

```bash
# Dry run (read-only)
python tests/test_uart_read_write_verify.py --port COM3 --dry-run

# Full test (will write to radio)
python tests/test_uart_read_write_verify.py --port COM3 --channels 5 --yes
```

## Documentation

- Technical docs go in `docs/`
- Keep README.md focused on user-facing info
- Update TODO.md with progress

## Questions?

- Open an issue for questions
- Check existing documentation in `docs/`

---

Thank you for contributing! 🎉
