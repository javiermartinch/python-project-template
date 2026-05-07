## Context & Motivation

<!-- Why is this change necessary? What problem does it solve? -->

**Linked Issue:** Fixes #<!-- issue number -->

## Description

<!-- Concise summary of the changes. -->

## Engineering Checklist (Blocking)

- [ ] Code maintains or increases 100% code coverage.
- [ ] Pydantic v2 schemas and static documentation (OpenAPI/JSON Schema) are updated if applicable.
- [ ] Public API signature changes are strictly backward-compatible (Semantic Versioning).
- [ ] Local static analysis passes: `uv run ruff check .` and `uv run pyright`.
- [ ] New dependencies (if any) are justified and added to `pyproject.toml`.

## Impact & Performance Analysis

<!-- Required for O(n)+ mutations or network integrations:
     Provide benchmarks, memory profiles, or algorithmic complexity justification. -->
