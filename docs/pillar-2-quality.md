# Pillar 2 — Iron Wall of Quality

> **Files involved:**
> `pyproject.toml` (sections `[tool.ruff]`, `[tool.pyright]`) ·
> `.pre-commit-config.yaml`

Static analysis is the code's first line of defense. It acts as a **cybernetic iron
wall** that detects security vulnerabilities, performance degradations, type errors,
and architectural drifts — all in milliseconds, before the code even reaches CI.

This pillar replaces a fragmented stack of legacy tools with just two:

| Before (fragmented) | Now (unified) |
|---|---|
| Flake8 (lint) + Black (format) + isort (imports) + Bandit (security) + pyupgrade + pydocstyle | **Ruff** (all-in-one, written in Rust) |
| mypy (type checker, slow, complex configuration) | **Pyright** (strict, fast, better inference) |

---

## 2.1 Ruff — Unified Linter and Formatter

### What Is It?

[**Ruff**](https://docs.astral.sh/ruff/) is a Python linter and formatter written in
Rust. It reimplements over 800 rules from dozens of independent tools, running
10-100x faster. A repository with 500,000 lines of code that took 30 seconds with
Flake8+Black is analyzed in under 1 second with Ruff.

### The Philosophy: `select = ["ALL"]`

The template activates **all available rules** and then surgically disables only
those that generate conflicts:

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",   # Trailing comma — the formatter handles it
    "ISC001",   # Direct conflict with the formatter
    "D203",     # Conflict with D211 (Google convention)
    "D213",     # Conflict with D212 (Google convention)
    # ... (full list in pyproject.toml)
]
```

**Why not list individual categories?** Because when Ruff adds new rules in updates,
a project with `select = ["ALL"]` receives them automatically. A project that lists
`["E", "F", "I", "UP", ...]` must maintain that list manually and misses new rules
until someone adds them.

### Rule Categories Included

This is a selection of the most relevant categories (Ruff includes 800+ rules):

| Category | Code | What Does It Detect? |
|-----------|--------|----------------|
| **pycodestyle** | `E`, `W` | [PEP 8](https://peps.python.org/pep-0008/) style errors and warnings |
| **pyflakes** | `F` | Unused variables, duplicate imports, name errors |
| **isort** | `I` | Incorrect import ordering and grouping |
| **pyupgrade** | `UP` | Obsolete syntax that can be modernized (e.g., `Union[X, Y]` → `X \| Y`) |
| **flake8-bugbear** | `B` | Bug-prone patterns (e.g., mutable default arguments) |
| **flake8-bandit** | `S` | **Security**: obsolete encryption, insecure deserialization, exposed tokens |
| **flake8-annotations** | `ANN` | Missing type annotations on public functions |
| **mccabe** | `C90` | Excessive cyclomatic complexity |
| **pylint** | `PL` | Pylint rules (too many arguments, nested blocks, etc.) |
| **perflint** | `PERF` | Performance inefficiencies (redundant calls in loops) |
| **flake8-simplify** | `SIM` | Code that can be simplified (e.g., `if x == True` → `if x`) |
| **flake8-boolean-trap** | `FBT` | Positional boolean arguments (API anti-pattern) |
| **eradicate** | `ERA` | Commented-out code that should be removed |
| **Ruff-specific** | `RUF` | Ruff-exclusive rules for modern patterns |
| **pydocstyle** | `D` | Missing or malformed docstrings |
| **flake8-type-checking** | `TCH` | Imports only used for type checking (optimization) |
| **flake8-use-pathlib** | `PTH` | Recommends `pathlib.Path` over `os.path` |

### Per-File Exceptions (`per-file-ignores`)

Not all rules make sense in every file. The template defines surgical exceptions:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",     # assert is pytest's primary tool
    "PLR2004",  # Magic values (assert x == 42) are normal in tests
    "ANN",      # Don't require type annotations in tests
    "D",        # Don't require docstrings in tests
    "FBT",      # Positional booleans OK in test helpers
    "ARG",      # Unused arguments (pytest fixtures)
    "SLF001",   # Private member access is legitimate in tests
]
"__init__.py" = [
    "F401",     # Re-exporting symbols without using them directly
]
```

**Why?** Tests have a different contract than production code. Requiring docstrings
in `test_main.py` or forbidding `assert` in pytest would be counterproductive. The
key is being strict where it matters and pragmatic where it doesn't.

### Complementary Configurations

```toml
[tool.ruff.lint.mccabe]
max-complexity = 10          # No function can have more than 10 paths
```

**Cyclomatic complexity** measures the number of independent paths through a function.
A value of 10 means that if a function has more than 10 combinations of
`if/else/for/while`, Ruff rejects it. This forces decomposition into smaller,
testable functions.

```toml
[tool.ruff.lint.isort]
known-first-party = ["my_package"]    # Your own modules
```

This tells the import organizer which modules are "yours" to group them correctly:

```python
# Before (unordered):
import os
from my_package.main import greet
import pydantic

# After (organized by isort):
import os                          # ← stdlib

import pydantic                    # ← third-party

from my_package.main import greet  # ← first-party
```

The `combine-as-imports = true` and `force-sort-within-sections = true` directives
further tighten the ordering: `as`-imports are combined into single lines, and
imports within each section are sorted strictly alphabetically.

```toml
[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"
```

**Relative imports** (`from .utils import foo`) are banned. All imports must use
absolute paths (`from my_package.utils import foo`). Relative imports introduce
subtle failure modes during refactoring: moving a file to a different directory
silently breaks all its relative imports without any static analysis warning.
Absolute imports make the dependency graph explicit and refactoring-safe.

```toml
[tool.ruff.lint.flake8-type-checking]
strict = true
```

This setting enforces that imports used **only** for type annotations are placed
inside an `if TYPE_CHECKING:` block ([flake8-type-checking docs](https://github.com/snok/flake8-type-checking)).
This optimization prevents circular import errors and reduces the module's runtime
import footprint, since `TYPE_CHECKING` is `False` at runtime.

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"
```

Docstrings follow the [Google convention](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.
    """
```

### Ruff as Formatter

Ruff also replaces **Black** as the formatter. The configuration defines the style:

```toml
[tool.ruff.format]
quote-style = "double"              # Always double quotes
indent-style = "space"              # Spaces, not tabs
skip-magic-trailing-comma = false   # Respect trailing commas
line-ending = "auto"                # Auto-detect
docstring-code-format = true        # Format code blocks inside docstrings
docstring-code-line-length = 80     # Narrower limit for docstring code blocks
```

The `docstring-code-format` directive instructs the formatter to parse and
reformat Python code blocks embedded within docstrings. This ensures that
code examples in documentation remain consistent with the project's formatting
standards. The `docstring-code-line-length` is set to 80 characters (narrower
than the project's 120-character line length) to account for the indentation
overhead inherent to docstring code blocks.

The maximum line length is defined globally:

```toml
[tool.ruff]
line-length = 120    # 88 is Black's default; 120 is modern for current monitors
```

---

## 2.2 Pyright — Strict Static Typing

### What Is It?

[**Pyright**](https://microsoft.github.io/pyright/) is a static type checker for
Python developed by Microsoft. It is the engine that powers Pylance in VS Code.
It operates in `strict` mode in this template, meaning **zero tolerance** for
ambiguous types.

### Why Not mypy?

| Aspect | mypy | Pyright |
|---------|------|---------|
| **Speed** | Slow (pure Python with optional C cache) | Fast (TypeScript/Node.js) |
| **Inference** | Basic (requires many manual annotations) | Advanced (infers complex types automatically) |
| **Strict mode** | Multiple independent flags | A single `"strict"` that activates everything |
| **Modern PEPs** | Slow adoption | Immediate support for new PEPs |
| **IDE integration** | Separate | Native (it is the Pylance engine) |

### What Does `strict` Mode Do?

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

Strict mode activates dozens of simultaneous checks:

| Check | What It Requires |
|---|---|
| **No implicit `Any`** | Every variable, parameter, and return must have a known type |
| **Complete annotations** | All public functions must have annotated parameters and return types |
| **Null safety** | Optional values (`Optional[T]`) must be checked with `is not None` before use |
| **No blind type: ignore** | If you use `# type: ignore`, you must specify the exact error code |
| **Required stubs** | Libraries without type stubs are reported (disabled in this template for pragmatism) |

### Template Configuration

```toml
[tool.pyright]
include = ["src", "tests"]              # Only analyze these folders
exclude = ["**/__pycache__", "**/.venv"] # Never analyze these
pythonVersion = "3.12"                   # Target version
typeCheckingMode = "strict"              # Maximum severity

# Pragmatic overrides:
reportMissingTypeStubs = false           # Many libraries still don't have stubs
reportUnnecessaryTypeIgnoreComment = true # Remove obsolete type: ignore comments
reportMissingModuleSource = false        # Don't fail if a module's source is missing
```

**Why `reportMissingTypeStubs = false`?** In the real ecosystem, many third-party
libraries don't provide type stubs. Forcing their existence would block development
without justification. It is a **pragmatic** decision within a strict framework.

### The Complete Type Flow: Pyright + Pydantic

The type system in this template works in two complementary layers:

| | Development Time | | Runtime |
|---|---|---|---|
| **Tool** | Pyright (strict) | **→ Build →** | Pydantic v2 (Rust) |
| **Verifies** | Source code contracts | | Real input data |
| **Guarantees** | No implicit `Any`, null safety | | Type coercion, rejection of invalid data |

Pyright guarantees that the **source code** is correct. Pydantic guarantees that
**input data** at runtime complies with the same contracts.

---

## 2.3 Pre-commit Hooks — Local Defense

### What Are They?

[Pre-commit](https://pre-commit.com/) hooks are scripts that run **automatically before every `git commit`**.
If any hook fails, the commit is blocked. The goal is that no defective code ever
reaches CI, saving compute time and latency.

### The Version Drift Problem

In collaborative projects, a classic problem is **version drift**:

```
pyproject.toml says:    ruff >= 0.11
uv.lock pins:          ruff == 0.15.8
.pre-commit-config.yaml says: ruff == 0.12.0  ← DIFFERENT VERSION!
```

The developer runs Ruff 0.12.0 in their commit, but CI runs 0.15.8. Rules may
have changed between versions, causing false positives or false negatives.

### The Solution: Local Hooks Aligned with `uv.lock`

The template **does not download** Ruff or Pyright from remote pre-commit repositories.
Instead, it uses `repo: local` to run tools through `uv run`:

```yaml
- repo: local
  hooks:
    - id: ruff-check
      entry: uv run ruff check --fix --exit-non-zero-on-fix
      language: system
```

`uv run` guarantees that **exactly** the version of Ruff pinned in `uv.lock` is
executed. This eliminates version drift by design:

- No redundant downloads (uses uv's global cache)
- Instant execution
- `uv sync` updates both the environment and the hooks automatically

### Hook Execution Order

```
git commit
    │
    ▼
┌─────────────────────────────────────┐
│ 1. uv-lock                         │  ← Is uv.lock synchronized?
├─────────────────────────────────────┤
│ 2. ruff check --fix                │  ← Lint + auto-fix
├─────────────────────────────────────┤
│ 3. ruff format                     │  ← Automatic formatting
├─────────────────────────────────────┤
│ 4. pyright                         │  ← Strict type checking
└─────────────────────────────────────┘
    │
    ▼
  Commit accepted (or rejected)
```

### Installation

```bash
uv run pre-commit install    # Registers hooks in .git/hooks/
```

This command is only run once. From that point on, hooks run automatically on
every `git commit`.

---

## 2.4 The Formatter as Style Dictator

### Why an Automatic Formatter?

In elite engineering, **style is not debated among humans**. The formatter has the
final word. This has three consequences:

1. **Code reviews focus on design, not style.** Nobody spends cognitive energy
   arguing whether a line should be 80 or 120 characters.

2. **Diffs are minimal.** If everyone uses the same formatter, whitespace changes
   disappear from Pull Requests.

3. **Onboarding is instant.** A new developer runs `uv run ruff format .` and
   their code meets all conventions without reading a style guide.

---

## Pillar 2 Summary

| Layer | Tool | What Does It Protect? | When Does It Run? |
|------|-------------|----------------|----------------------|
| **Lint** | Ruff (800+ rules) | Bugs, security, performance, style | Pre-commit + CI |
| **Format** | Ruff (formatter) | Visual code consistency | Pre-commit + CI |
| **Types** | Pyright (strict) | Type errors, null safety, contracts | Pre-commit + CI |
| **Runtime** | Pydantic v2 | Corrupt input data | Execution |
| **Lockfile** | uv-lock hook | pyproject.toml ↔ uv.lock synchronization | Pre-commit |

[← Pillar 1: Architecture](pillar-1-architecture.md) · [Next: Pillar 3 — CI/CD →](pillar-3-ci-cd.md)
