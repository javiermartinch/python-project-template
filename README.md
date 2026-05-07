# 🚀 Python Professional Project Template

> Production-ready Python project scaffolding — Copier template with
> uv, Ruff, Pyright (strict), hatch-vcs, GitHub Actions CI/CD,
> MkDocs Material, and Trunk-Based Development.

[![CI](https://github.com/javiermartinch/python-project-template/actions/workflows/ci.yml/badge.svg)](https://github.com/javiermartinch/python-project-template/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)](https://www.python.org/)
[![Checked with Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Copier](https://img.shields.io/badge/copier-template-blue)](https://copier.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Quick Start

```bash
# Install Copier once
uv tool install copier

# Generate the project
copier copy gh:javiermartinch/python-project-template my-new-project
cd my-new-project

# Initialize and install
git init && git branch -M main
uv lock
uv sync --dev
uv run pre-commit install
git add . && git commit -m "chore: initialize project" && git tag v0.1.0
```

Need the full wizard reference, granular feature toggles, or local docs preview
commands? See [docs/quick-start.md](docs/quick-start.md) or the published
documentation site below.

## What You Get

This template generates a fully configured Python project with:

- **Build Backend:** `hatchling` + `hatch-vcs` (Git tag versioning)
- **Package Manager:** `uv`
- **Linting & Formatting:** `Ruff`
- **Type Checking:** `Pyright` (Strict mode)
- **Testing:** `pytest` + `pytest-cov` (100% enforcement)
- **CI/CD:** GitHub Actions (Static Analysis, Test Matrix, Publish to PyPI via OIDC)
- **Documentation:** MkDocs Material
- **Dependency Management:** Renovate configuration
- **GitHub Config:** PR templates, issue templates, release drafter

## Documentation

Full architectural documentation explaining the "why" behind every configuration is available at:
https://javiermartinch.github.io/python-project-template

## License

This template is licensed under the MIT License — © Javier Martín-Chávez.
Generated projects use the license you choose during setup.
