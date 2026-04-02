# Quick Start Guide — Step by Step

This guide takes you from zero to a fully functional project using this template via [Copier](https://copier.readthedocs.io/).

---

## Prerequisites

Before starting, you need:

| Tool | Installation | Verification |
|-------------|-------------|--------------|
| **Git** | [git-scm.com](https://git-scm.com/) | `git --version` |
| **Python 3.12+** | [python.org](https://www.python.org/) or `uv python install 3.12` | `python --version` |
| **uv** | Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh \| sh`<br>Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `uv --version` |
| **copier** | `uv tool install copier` | `copier --version` |

---

## Phase 1 — Create the Project (Pillar 1)

### Step 1: Generate the Project

Run Copier and point it to the template repository:

```bash
copier copy gh:javiermartinch/python-project-template my-new-project
```

Copier starts in one of two modes:

- **Standard Elite 2026 (Recommended):** Generates the full opinionated stack with GitHub integration, docs, tests, pre-commit, CI, PyPI publishing, and Renovate enabled by default.
- **Custom Selection (Granular control):** Exposes the optional components so you can disable GitHub files, docs, tests, pre-commit hooks, CI, PyPI publishing, or Renovate.

The wizard prompts are:

| Prompt | When shown | Meaning |
|---|---|---|
| `config_wizard` | Always | Select the recommended full stack or granular mode |
| `project_name` | Always | Distribution name in lowercase kebab-case |
| `package_name` | Always | Import package name; defaults to `project_name` with underscores |
| `project_description` | Always | Short project summary |
| `author_name` / `author_email` | Always | Package metadata and ownership |
| `license` | Always | SPDX license for the generated project |
| `github_org` | Standard mode, or when GitHub/docs are enabled | Used for repository and documentation URLs |
| `include_github` | Custom mode | Include `.github/` files for repository governance |
| `include_docs` | Custom mode | Include MkDocs documentation |
| `include_tests` | Custom mode | Include `tests/` and pytest coverage configuration |
| `include_pre_commit` | Custom mode | Include `.pre-commit-config.yaml` |
| `include_ci` | Custom mode when GitHub is enabled | Include the GitHub Actions CI workflow |
| `include_pypi_publish` | Custom mode when GitHub is enabled | Include OIDC publishing to PyPI |
| `include_renovate` | Custom mode when GitHub is enabled | Include `renovate.json` for dependency updates |

By the end, Copier will scaffold a ready-to-use project inside `my-new-project/`.

### Step 2: Initialize Git and Generate Lockfile

```bash
cd my-new-project

# Initialize a fresh git repository
git init
git branch -M main

# Generate uv.lock and install development dependencies into .venv
uv lock
uv sync --dev
```

### Step 3: Verify the Base

Run the baseline validation pipeline:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

If you kept the test suite enabled, also run:

```bash
uv run pytest --cov=src
```

> **First Tag:** Create an initial tag early to satisfy `hatch-vcs` versioning:
> ```bash
> git add .
> git commit -m "chore: initial project generation via copier"
> git tag v0.1.0
> ```

---

## Phase 2 — Optional Project Setup

If you disabled GitHub, docs, tests, or pre-commit in custom mode, skip the
steps that do not apply to your generated profile.

1. **Pre-commit:** Install local hooks if you included pre-commit support.
   ```bash
   uv run pre-commit install
   ```
2. **Local docs preview:** If you included documentation, install the docs group and serve the site locally.
   ```bash
   uv sync --group docs --dev
   uv run mkdocs serve
   ```
3. **Push to GitHub:** If you included GitHub repository files, create the remote repository and push.
   ```bash
   gh repo create your-org/my-new-project --private --source=. --push
   ```
4. **Branch protection:** Protect `main` and require the CI status checks that match your generated profile.
5. **Publishing:** If you included `publish.yml`, configure PyPI Trusted Publishers before cutting your first release.

For more information, explore the [Pillars documentation](index.md).
