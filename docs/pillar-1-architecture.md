# Pillar 1 — Architecture and Environment

> **Files involved:**
> `pyproject.toml` · `src/` · `tests/` · `uv.lock` · `py.typed`

This pillar defines the project's foundation: how the code is organized, how it is
packaged, how dependencies are managed, and how to guarantee that the environment
is identical for all developers and across all systems.

---

## 1.1 Src Layout — Project Topology

### What Is It?

The **[src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)** is an organizational convention recommended by the PyPA where all importable package code
lives inside a `src/` subdirectory, physically separated from tests, configuration,
and auxiliary scripts.

```
project/
├── src/
│   └── my_package/      ← Importable code (this is what gets published)
│       ├── __init__.py
│       ├── py.typed
│       └── main.py
├── tests/               ← Tests (never published or imported)
├── pyproject.toml        ← Configuration (not importable)
└── uv.lock
```

### Why Not Flat Layout?

In a flat layout (`my_package/` directly at root), the project's root directory
is implicitly added to `sys.path`. This creates three serious problems:

| Problem | Flat Layout | Src Layout |
|---------|-------------|------------|
| **Import contamination** | Python can import configuration files (`conftest.py`, `tox.ini`) as if they were package modules | Only what is explicitly inside `src/` can be imported |
| **False confidence in tests** | Tests pass locally because they import directly from the working directory, but fail from PyPI because a submodule was not included in the wheel | Tests run against the *installed* package, replicating exactly what the end user receives |
| **Non-deterministic packaging** | The build backend may accidentally include junk files | `src/` defines an explicit boundary: everything inside is packaged, nothing else |

### The `py.typed` File (PEP 561)

```
src/my_package/py.typed    ← Empty file, but MANDATORY
```

This empty file formally declares that the package supports static typing per
[PEP 561](https://peps.python.org/pep-0561/). Without this file:

- Pyright, mypy and other type checkers **ignore** the package's type annotations
  when used by external projects.
- Users of your library get no autocompletion or type checking in their editors.

It is literally a zero-byte file that unlocks the entire type system for your
package's consumers.

### Test Structure

```
tests/
├── __init__.py          ← Needed for pytest to discover tests
├── conftest.py          ← Shared fixtures across all tests
├── unit/                ← Fast tests, no external dependencies
│   └── test_main.py
└── integration/         ← Tests requiring network, DB, or external services
    └── (empty for now)
```

The `unit/` vs `integration/` separation enables selective execution:

```bash
uv run pytest tests/unit/                 # Unit tests only (fast)
uv run pytest tests/integration/          # Integration tests only
uv run pytest -m "not slow"               # Exclude tests marked as slow
```

---

## 1.2 `pyproject.toml` — Single Source of Truth

### What Is It?

`pyproject.toml` is the centralized configuration file standardized by
[PEP 621](https://peps.python.org/pep-0621/) (metadata) and
[PEP 517](https://peps.python.org/pep-0517/) (build system). In this template,
it **completely replaces**:

| Legacy File | Section in `pyproject.toml` |
|---|---|
| `setup.py` / `setup.cfg` | `[project]` + `[build-system]` |
| `requirements.txt` | `[project.dependencies]` + `[dependency-groups]` |
| `.flake8` / `tox.ini` | `[tool.ruff]` |
| `mypy.ini` / `pyrightconfig.json` | `[tool.pyright]` |
| `pytest.ini` / `conftest.py` (config) | `[tool.pytest.ini_options]` |
| `.coveragerc` | `[tool.coverage.*]` |

### Section-by-Section Anatomy

#### `[build-system]` — Build Engine

```toml
[build-system]
requires = ["hatchling>=1.28", "hatch-vcs>=0.4"]
build-backend = "hatchling.build"
```

- **[`hatchling`](https://hatch.pypa.io/latest/)** is the build backend recommended by the PyPA. It is fast, compliant
  with all modern PEPs, and has minimal configuration.
- **[`hatch-vcs`](https://github.com/ofek/hatch-vcs)** is a Hatchling plugin that derives the package version
  from Git tags at build time (see [Section 1.2.1](#121-dynamic-versioning-hatch-vcs)).
- `requires` declares what is needed to **build** the package (not to run it).
- `build-backend` tells tools like `uv build` or `pip wheel` which Python module
  to invoke to generate the sdist and wheel.

#### `[project]` — Package Metadata (PEP 621)

```toml
[project]
name = "my-package"
dynamic = ["version"]
requires-python = ">=3.12"
dependencies = ["pydantic>=2.10"]
```

| Field | Purpose |
|-------|---------|
| `name` | Name on PyPI. Must be globally unique. Use hyphens (`my-package`), not underscores. |
| `dynamic` | Lists fields whose values are determined at build time. The version is derived from Git tags via `hatch-vcs` (see below). |
| `requires-python` | Minimum Python version. `>=3.12` ensures access to `type` statements, `@override`, etc. |
| `dependencies` | **Runtime** dependencies. Only what the end user needs. |

#### `[tool.hatch.version]` — Dynamic Versioning (hatch-vcs) {#121-dynamic-versioning-hatch-vcs}

```toml
[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/my_package/_version.py"
```

The template uses **[hatch-vcs](https://github.com/ofek/hatch-vcs)** to derive the package version from
Git tags rather than maintaining a hardcoded `version = "X.Y.Z"` string in `pyproject.toml`.

| Directive | Function |
|---|---|
| `source = "vcs"` | Instructs Hatchling to read the version from the VCS (Git) tag history. A tag `v1.2.0` produces version `1.2.0`. |
| `version-file` | At build time, hatch-vcs writes a `_version.py` file containing the resolved version string. This file is auto-generated and listed in `.gitignore`. |

The version is exposed at runtime via the standard `importlib.metadata` API
([Python docs](https://docs.python.org/3/library/importlib.metadata.html)):

```python
# src/my_package/__init__.py
from importlib.metadata import version

__version__ = version("my-package")
```

This approach has three operational advantages:

1. **No manual version bumping.** The release workflow is: `git tag v1.2.0 && git push --tags`.
2. **Single source of truth.** The Git tag is the canonical version; `pyproject.toml`,
   the wheel metadata, and `__version__` all derive from it.
3. **Dev versions are automatic.** Between tags, hatch-vcs generates versions like
   `1.2.0.dev3+g1a2b3c4`, encoding the distance from the last tag and the commit hash.

#### `[tool.hatch.build.targets.wheel]` — Package Boundary

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

This directive explicitly tells Hatchling where the packageable code is.
Without it, the build backend could use heuristics that include unnecessary files.

#### `[dependency-groups]` — Development Dependencies (PEP 735)

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=6.0",
    "pyright>=1.1.400",
    "ruff>=0.11",
    "pre-commit>=4.0",
]
```

Unlike `[project.optional-dependencies]` (extras), **dependency groups**
([PEP 735](https://peps.python.org/pep-0735/)) are exclusively for development. They are not included in the final
package distribution nor available via `pip install my-package[dev]`. This is
deliberate: the maintainer's development tools must not pollute the end user.

They are installed with:
```bash
uv sync --dev           # Installs the project + "dev" group
```

---

## 1.3 `uv` — Unified Package and Environment Manager

### What Is It?

[**uv**](https://docs.astral.sh/uv/) is a package manager, virtual environment manager,
and Python project manager written in Rust by Astral (the creators of Ruff). It
**simultaneously replaces**:

| Replaced Tool | Functionality |
|---|---|
| `pip` | Package installation |
| `pip-tools` | Dependency compilation and locking |
| `virtualenv` / `venv` | Virtual environment creation |
| `poetry` | Project management and lockfiles |
| `pipx` | Isolated tool execution |

### Why uv and Not pip/Poetry?

1. **Speed:** 10-100x faster than pip. Resolving and installing 500 packages takes
   seconds, not minutes.
2. **Deterministic lockfile:** `uv.lock` captures an exact cross-platform dependency
   graph. Resolution is identical on Linux, macOS, Windows, x86, and ARM.
3. **Global cache:** Deduplicates packages at the OS level. If two projects
   use `pydantic==2.10.6`, the package exists only once on disk.
4. **Interoperability:** Respects all packaging PEPs. Not a closed ecosystem
   like Poetry.

### Essential Commands

```bash
# Create lockfile from pyproject.toml
uv lock

# Install everything (project + dev dependencies) in an automatic venv
uv sync --dev

# Run a command within the project environment
uv run pytest
uv run ruff check .

# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --group dev hypothesis

# Build the package (sdist + wheel)
uv build
```

---

## 1.4 `uv.lock` — Mathematical Reproducibility

### What Is It?

The `uv.lock` file is a **cross-platform, deterministic lockfile**. It captures the
complete dependency graph resolution: every package, every exact version, every
integrity hash, for every combination of OS + architecture + Python version.

### How Does It Differ from `requirements.txt`?

| Aspect | `requirements.txt` | `uv.lock` |
|---------|---------------------|-----------|
| **Scope** | Only the dependencies of the environment where it was generated | All platforms simultaneously |
| **Determinism** | Partial (depends on the pip resolver at the time) | Total (identical resolution always) |
| **Transitivity** | Requires manual `pip freeze` | Automatically captures the complete graph |
| **Integrity** | No hashes by default | Hashes for every artifact |

### CI Rule: `--locked`

In CI, the `--locked` flag is **always** used:

```bash
uv sync --locked --dev    # Fails if uv.lock doesn't match pyproject.toml
```

This prevents a developer from modifying `pyproject.toml` (e.g., adding a
dependency) but forgetting to run `uv lock` to update the lockfile. Without this
check, CI could resolve different dependencies from what the developer tested locally.

### Should `uv.lock` Be Committed?

**Yes, always.** The lockfile is an integral part of the repository. It guarantees
that the exact version of every dependency is the same for:

- All developers on the team
- Every CI run
- The final build published to PyPI

---

## 1.5 Pydantic v2 — Runtime Validation

### What Is It?

[Pydantic v2](https://docs.pydantic.dev/latest/) is a data validation library
with a core written in Rust (`pydantic-core`). It is a **runtime** dependency
(not a development one) because it closes a fundamental gap in Python's type system:
**type erasure** at runtime.

### The Problem It Solves

Python does not preserve types at runtime. Static analysis (Pyright) verifies types
**before** executing the code, but it does not protect against corrupt data arriving
at runtime (APIs, databases, JSON files, environment variables).

```python
# Pyright verifies this during development ✓
def process(data: UserData) -> None: ...

# But at runtime, Python doesn't validate that `raw_json` has the correct shape
data = json.loads(raw_json)  # ← This is dict[str, Any], could be anything
process(data)                # ← Pyright can't protect you here
```

### The Solution: Validation at the Boundary

```python
from pydantic import BaseModel, Field

class UserData(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=150)

# Automatic validation: if the JSON doesn't match the schema, it fails IMMEDIATELY
data = UserData.model_validate_json(raw_json)
# From this point on, data.name is str and data.age is int — guaranteed
```

Pydantic enforces that **external data** entering the system complies with the same
contracts defined through type annotations. It's the runtime counterpart to Pyright.
