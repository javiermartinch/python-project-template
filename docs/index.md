# Python Project Template 2026

This template codifies the elite engineering standard for Python repositories in 2026.
Every file, every configuration, and every workflow exists to solve a specific problem
of quality, security, or maintainability. There is no decorative configuration.

---

## The Five Pillars

The documentation is organized into **five fundamental pillars** that represent the
major architectural blocks of any professional Python project:

| Pillar 1 | Pillar 2 | Pillar 3 | Pillar 4 | Pillar 5 |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture & Env.** | **Quality & Standards** | **CI & CD Pipeline** | **Governance & Community** | **Maintenance & Delivery** |
| `pyproject.toml` | `ruff` | `ci.yml` | `CODEOWNERS` | `renovate.json` |
| `src/` layout | `pyright` | `publish.yml` | `SECURITY.md` | `release-drafter.yml` |
| `uv.lock` | `pre-commit` | `test matrix` | `PR_TEMPLATES` | `Conventional Commits` |
| `pydantic v2` | | `100% coverage` | `ISSUE_TEMPLATES` | `Semantic Versioning` |

---

## Documentation Index

<div class="grid cards" markdown>

-   :material-pillar:{ .lg .middle } **Pillar 1 — Architecture and Environment**

    ---

    Src layout, `pyproject.toml`, `uv`, lockfiles, build backend, Pydantic v2

    [:octicons-arrow-right-24: Read](pillar-1-architecture.md)

-   :material-shield-check:{ .lg .middle } **Pillar 2 — Iron Wall of Quality**

    ---

    Ruff (linter+formatter), Pyright (strict typing), pre-commit hooks

    [:octicons-arrow-right-24: Read](pillar-2-quality.md)

-   :material-sync:{ .lg .middle } **Pillar 3 — Continuous Integration and Delivery**

    ---

    GitHub Actions, test matrix, 100% coverage, OIDC publishing to PyPI

    [:octicons-arrow-right-24: Read](pillar-3-ci-cd.md)

-   :material-account-group:{ .lg .middle } **Pillar 4 — Governance and Community**

    ---

    CODEOWNERS, PR templates, issue templates, SECURITY.md, Git workflow

    [:octicons-arrow-right-24: Read](pillar-4-governance.md)

-   :material-wrench:{ .lg .middle } **Pillar 5 — Maintenance and Delivery**

    ---

    Renovate, Release Drafter, Semantic Versioning, Conventional Commits

    [:octicons-arrow-right-24: Read](pillar-5-maintenance.md)

-   :material-rocket-launch:{ .lg .middle } **Quick Start — Step by Step**

    ---

    Complete checklist to use this template for a new project

    [:octicons-arrow-right-24: Read](quick-start.md)

</div>

---

## File → Pillar Map

Every file in the repository belongs to one or more pillars. This table serves as a
quick reference to understand **why each file exists**.

```
.
├── .github/                      ← Real governance of the template
│   ├── CODEOWNERS
│   ├── release-drafter.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   └── workflows/                ← Root repository workflows (CI, docs, release drafter)
├── copier.yml                    ← Copier configuration and questions
├── docs/                         ← This documentation
├── template/                     ← GENERATED CONTENT
│   ├── pyproject.toml.jinja
│   ├── README.md.jinja
│   ├── .pre-commit-config.yaml
│   ├── renovate.json
│   ├── .github/                  ← Generated project governance
│   ├── src/
│   └── tests/
├── mkdocs.yml                    ← MkDocs configuration
├── pyproject.toml                ← Dependencies for docs only
├── SECURITY.md
├── LICENSE
└── README.md                     ← Template repository README
```

---

## Guiding Principles

These principles underpin every architectural decision in the template:

1. **Single Source of Truth** — `pyproject.toml` is the only configuration file.
   There are no separate `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, or `requirements.txt` files.

2. **Rust Tools over Python** — Ruff and uv, written in Rust, are 10-100x faster
   than their predecessors (Flake8, Black, pip, Poetry). Speed is not a luxury;
   it reduces CI latency, compute costs, and development friction.

3. **Fail Fast** — Errors are detected as early as possible: first in the editor,
   then in pre-commit, then in CI. Expensive tests only run if static analysis passes.

4. **Mathematical Reproducibility** — `uv.lock` guarantees identical builds on any
   machine, OS, and architecture. No "works on my machine".

5. **Zero Trust in Publishing** — Publishing to PyPI uses ephemeral 15-minute OIDC
   tokens. There are no long-lived secrets to rotate or that could be leaked.

6. **Total Automation** — Changelogs, semantic versioning, dependency updates, and
   publishing are automated processes. If a human does it manually, it is an
   architectural defect.

---

## Official References

All standards, tools, and PEPs cited in this documentation:

### Python Enhancement Proposals (PEPs)

| PEP | Title |
|-----|-------|
| [PEP 8](https://peps.python.org/pep-0008/) | Style Guide for Python Code |
| [PEP 517](https://peps.python.org/pep-0517/) | A build-system independent format for source trees |
| [PEP 561](https://peps.python.org/pep-0561/) | Distributing and Packaging Type Information |
| [PEP 621](https://peps.python.org/pep-0621/) | Storing project metadata in pyproject.toml |
| [PEP 735](https://peps.python.org/pep-0735/) | Dependency Groups in pyproject.toml |
| [PEP 740](https://peps.python.org/pep-0740/) | Index support for digital attestations |

### Core Tools

| Tool | Official Documentation |
|------|----------------------|
| uv | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Ruff | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/) |
| Pyright | [microsoft.github.io/pyright](https://microsoft.github.io/pyright/) |
| Hatchling | [hatch.pypa.io](https://hatch.pypa.io/latest/) |
| hatch-vcs | [github.com/ofek/hatch-vcs](https://github.com/ofek/hatch-vcs) |
| Pydantic v2 | [docs.pydantic.dev](https://docs.pydantic.dev/latest/) |
| pytest | [docs.pytest.org](https://docs.pytest.org/) |
| coverage.py | [coverage.readthedocs.io](https://coverage.readthedocs.io/) |
| pre-commit | [pre-commit.com](https://pre-commit.com/) |

### Standards and Practices

| Standard | Reference |
|----------|-----------|
| Semantic Versioning | [semver.org](https://semver.org/) |
| Conventional Commits | [conventionalcommits.org](https://www.conventionalcommits.org/) |
| Trunk-Based Development | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) |
| src layout (PyPA) | [packaging.python.org](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) |

### GitHub Actions and Integrations

| Action / App | Repository |
|-------------|-----------|
| astral-sh/setup-uv | [github.com/astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) |
| pypa/gh-action-pypi-publish | [github.com/pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) |
| Release Drafter | [github.com/release-drafter/release-drafter](https://github.com/release-drafter/release-drafter) |
| Renovate | [docs.renovatebot.com](https://docs.renovatebot.com/) |
| CODEOWNERS | [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) |
| Trusted Publishers (PyPI) | [docs.pypi.org/trusted-publishers](https://docs.pypi.org/trusted-publishers/) |
