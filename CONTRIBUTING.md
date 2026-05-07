# Contributing to python-project-template

Thank you for your interest! This project is a **Copier template**.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [copier](https://copier.readthedocs.io/) (`uv tool install copier`)

## How it works

- The root of the repository is the **template itself** (its own docs, its own CI).
- The `template/` folder contains the **content generated** for users via Jinja2 templates.

## Local Testing

This repository has two validation layers:

1. **Root repository checks:** Validate the root docs and the template test harness.
2. **Generated project smoke tests:** Render a real project and verify that the generated stack boots cleanly.

### Fast Path — Match the Root CI Locally

Run this from the repository root before opening a PR:

```bash
uv sync --dev --group docs
uv run pre-commit run --all-files
uv run ruff check tests
uv run pyright tests
uv run mkdocs build --strict
uv run pytest -q
```

### Manual Debugging of a Generated Project

Use this only when you need to inspect the rendered output or reproduce a failing
generation scenario by hand:

```bash
# 1. Generate a test project outside the repository worktree
copier copy . ../sandbox/test-project --defaults -d project_name=test-project -d github_org=test-org

# 2. Go to the generated project and run the generated-project pipeline
cd ../sandbox/test-project
git init
git branch -M main
uv lock
uv sync --dev
uv run pre-commit install
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --cov=src
uv build
uv run python -c "from test_project import greet; print(greet('World'))"

# 3. If the generated profile includes docs, validate them explicitly
uv sync --group docs --dev
uv run mkdocs build --strict
```

The automated `uv run pytest -q` path already performs this smoke test for the
standard profile. Use the manual flow when debugging feature flags or inspecting
generated files.

## Creating a Pull Request

1. Fork and create a feature branch (`feat/...`, `fix/...`)
2. Make your modifications.
3. Run the local validation flow above.
4. Open a PR. The root `ci.yml` GitHub Actions workflow will run the repository checks automatically.
