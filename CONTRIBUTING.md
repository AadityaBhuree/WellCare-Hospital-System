# Contributing to WellCare Hospital Management System

Thank you for considering contributing to the WellCare Hospital Management System! This document outlines our code standards, development workflow, and pull request process.

## 🚀 Getting Started

1. **Fork & Clone** the repository:
   ```bash
   git clone https://github.com/AadityaBhuree/WellCare-Hospital-System.git
   cd WellCare-Hospital-System
   ```

2. **Set up virtual environment & dependencies**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate

   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## 🛠️ Development Guidelines

### Code Quality & Formatting
We strictly enforce code formatting and linting rules using `ruff` and type safety using `mypy`:
```bash
# Check linting and formatting
ruff check src/ tests/
ruff format --check src/ tests/

# Run static type checking
mypy src/
```

### Testing
All changes must be accompanied by unit or integration tests:
```bash
# Run tests with coverage
pytest tests/ -v --cov=src
```

### Git Commit Conventions
Follow standard Conventional Commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation updates
- `style:` for formatting/style changes
- `refactor:` for code restructuring without changing behavior
- `test:` for adding or updating tests
- `chore:` for maintenance tasks

## 📬 Submitting Pull Requests

1. Create a topic branch: `git checkout -b feature/my-new-feature`
2. Make your edits and pass all linter and pytest checks.
3. Commit with a clear commit message.
4. Push to your branch and open a Pull Request against `main`.
