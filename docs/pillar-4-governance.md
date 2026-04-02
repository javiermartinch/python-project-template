# Pillar 4 — Governance and Community

> **Files involved:**
> `.github/CODEOWNERS` · `.github/PULL_REQUEST_TEMPLATE.md` ·
> `.github/ISSUE_TEMPLATE/` · `SECURITY.md` · `LICENSE` · `README.md`

The governance of a professional repository is not delegated to the good will of
maintainers. It is codified through **inflexible platform policies** and structured
templates that eliminate ambiguity and standardize communication.

---

## 4.1 CODEOWNERS — Algorithmic Code Ownership

### What Is It?

The [`CODEOWNERS`](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) file algorithmically defines **who is responsible for reviewing
changes** in each part of the repository. GitHub uses it to automatically assign
reviewers when a Pull Request is opened.

### Why Is It Critical?

Without CODEOWNERS, any developer with write access can approve any change.
This creates two risks:

1. **Out-of-domain approvals:** A frontend developer approves changes to the
   cryptography module without having the expertise to evaluate them.
2. **Diffuse responsibility:** If nobody is explicitly responsible, nobody
   feels obligated to review.

### Template Structure

```
# Default fallback — core maintainers own everything
* @your-org/core-maintainers

# Security-critical domains
/src/my_package/auth/    @your-org/security-team
/src/my_package/crypto/  @your-org/security-team

# Infrastructure and CI/CD
/pyproject.toml           @your-org/infra-team
/.github/workflows/       @your-org/infra-team
```

### How Does It Work?

| Rule | Meaning |
|-------|-------------|
| `* @your-org/core-maintainers` | **Fallback**: if no other rule matches, the core team reviews |
| `/src/my_package/auth/ @your-org/security-team` | Any change in the authentication module requires security team approval |
| `/pyproject.toml @your-org/infra-team` | Changes to dependencies or build configuration require infrastructure approval |

Rules are evaluated **top to bottom**; the last matching rule wins. That's why
the fallback `*` is first.

### Integration with Branch Protection

CODEOWNERS gains its true power when combined with `main` branch protection rules:

```
Pull Request with changes in /src/my_package/auth/login.py
    │
    ├── CI passes ✓ (lint, types, tests)
    ├── @your-org/security-team approves ✓
    │
    └── Only then does GitHub allow the merge
```

If the security team does not approve, the PR is **blocked** regardless of how
many approvals from other teams it has.

---

## 4.2 Git Workflow — Trunk-Based Development

### What Is It?

**[Trunk-Based Development](https://trunkbaseddevelopment.com/) (TBD)** is a branching strategy where all integrations
are directed to a single main branch (`main`). Feature branches are **ephemeral**
(lasting hours, not days) and small.

### Why Not GitFlow?

| Aspect | GitFlow | Trunk-Based Development |
|---------|---------|------------------------|
| **Active branches** | develop, release/*, hotfix/*, feature/* | main + ephemeral branches |
| **Integration latency** | Days or weeks | Hours |
| **Merge conflicts** | Frequent and massive | Rare and small |
| **Cognitive complexity** | High (which branch do I branch from? which do I merge to?) | Minimal (always from/to main) |
| **Suitable for** | Packaged software with long release cycles | Continuous delivery, SaaS, libraries |

### Branch Naming Convention

All branches originate from `main` and follow the pattern:

```
<type>/<short-description>
```

| Type | Purpose | Example |
|------|---------|---------|
| `feat/` | New functionality | `feat/user-authentication` |
| `fix/` | Bug fix | `fix/null-response-gateway` |
| `docs/` | Documentation changes | `docs/api-reference-v2` |
| `chore/` | Maintenance, CI, dependencies | `chore/bump-ruff-0.15` |
| `refactor/` | Code restructuring | `refactor/extract-validation` |
| `perf/` | Performance improvement | `perf/cache-db-queries` |
| `test/` | Adding or modifying tests | `test/edge-cases-parser` |

Rules:

- Use **lowercase** and **hyphens** as word separators (`fix/null-response`, not `fix/NullResponse` or `fix/null_response`).
- Keep names short and descriptive (2-4 words after the prefix).
- The branch type prefix should match the [Conventional Commits](#46-conventional-commits--commit-message-format) type used in the PR title.

### Complete Development Workflow

The following sequence documents the full lifecycle of a change, from branch
creation to merge:

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create an ephemeral branch
git checkout -b feat/invoice-validation

# 3. Develop iteratively (commit messages within the branch are informal)
#    These intermediate commits will be discarded by squash merge.
git add .
git commit -m "wip: initial invoice schema"
git add .
git commit -m "add validation rules"
git add .
git commit -m "fix test"

# 4. Run the quality pipeline locally before pushing
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --cov=src

# 5. Push the branch and open a Pull Request
git push -u origin feat/invoice-validation
```

At this point, open a Pull Request on GitHub. The PR title **must** follow the
[Conventional Commits](#46-conventional-commits--commit-message-format) format
because it becomes the final commit message on `main` after squash merge:

```
feat: add invoice validation schema (#87)
```

After CI passes and the required reviewers approve:

```bash
# 6. Squash Merge via GitHub UI (configured as the only merge strategy)
#    GitHub squashes all branch commits into a single commit on main.
#    The branch is automatically deleted after merge (configured in repository settings).

# 7. Update local main
git checkout main
git pull origin main
```

> **Note:** Commit messages within the feature branch do not need to follow
> Conventional Commits. They are discarded during squash merge. Only the
> **PR title** matters, as it becomes the commit message on `main`.

### Branch Lifecycle Rules

| Rule | Rationale |
|------|-----------|
| Always branch from `main` | Prevents cascading dependencies between branches |
| Maximum lifetime: **48 hours** | Long-lived branches accumulate merge conflicts |
| Maximum scope: **one logical change** | A branch that touches authentication and billing should be two branches |
| Delete after merge | Automatic via GitHub setting "Automatically delete head branches" |
| Never reuse a branch name | After deletion, create a new branch with a new name |

### Fundamental `main` Protection Rules

These rules must be configured in GitHub (Settings → Rules → Rulesets):

| Rule | Effect |
|-------|--------|
| `required_pull_request_reviews` | Forbids direct push to main. Everything goes through PRs. |
| `required_status_checks` | CI (lint, types, tests) must pass before merge. |
| `required_conversation_resolution` | All comment threads must be resolved. |
| `allow_force_pushes = false` | Forbids rewriting main's history. |
| `require_linear_history = true` | Requires linear history (squash merge). |

### Linear History and Squash Merge

TBD forbids conventional **merge commits**. Each PR is integrated exclusively
via **Squash Merge**, which collapses all commits in the branch into a single
atomic commit:

```
Branch feat/login:
  commit 1: "wip"
  commit 2: "fix typo"
  commit 3: "actually fix it"
  commit 4: "forgot import"

         │ Squash Merge
         ▼

main:
  commit abc123: "feat: add login endpoint (#42)"
    ← A single clean commit, with the PR title
```

**Why?** When a regression occurs in production, `git bisect` searches for the
exact commit that introduced the error. With linear history, bisection is
logarithmically efficient. With interleaved merge commits, `git bisect` often
lands on broken intermediate commits within historical branches.

---

## 4.3 Pull Request Template

### What Does It Solve?

A PR without structure destroys the reviewer's efficiency. The reviewer has to
invest extra time understanding **what**, **why**, and **in what state** the
change is before being able to evaluate it.

### Template Structure

```markdown
## Context & Motivation
<!-- WHY is this change necessary? -->
**Linked Issue:** Fixes #<number>

## Description
<!-- WHAT changed? Concise summary. -->

## Engineering Checklist (Blocking)
- [ ] Code maintains or increases 100% code coverage.
- [ ] Pydantic v2 schemas and documentation are updated if applicable.
- [ ] Public API changes are backward-compatible (SemVer).
- [ ] Local static analysis passes: uv run ruff check . && uv run pyright
- [ ] New dependencies are justified and added to pyproject.toml.

## Impact & Performance Analysis
<!-- For O(n)+ changes or network integrations -->
```

### Every Section Has a Purpose

| Section | Why? |
|---------|-----------|
| **Context & Motivation** | The reviewer needs to know the *why* before the *what*. Without context, a refactoring looks arbitrary. |
| **Linked Issue** | Traceability. The PR automatically closes the issue on merge (`Fixes #123`). |
| **Engineering Checklist** | Prevents opening immature PRs. If the author hasn't run lint/types locally, they shouldn't even open the PR. |
| **Impact & Performance** | Forces justification of non-trivial changes with data (benchmarks, algorithmic complexity). |

### Size Rule

The standard's heuristic dictates:

- **Optimal:** < 50 lines of code
- **Acceptable:** < 200 lines
- **Unacceptable:** > 200 lines (split into smaller PRs)

If a reviewer needs more than 15 minutes to understand a PR, the task should have
been decomposed.

---

## 4.4 Issue Templates

### What Are They?

Issue templates are structured YAML forms that guide the user to provide **all the
necessary information** when reporting a bug or requesting a feature. They eliminate
empty issues like *"it doesn't work"*.

### Bug Report (`bug_report.yml`)

Required form fields:

| Field | Type | Purpose |
|-------|------|---------|
| Description | textarea | Clear description of the bug |
| Steps to Reproduce | textarea | Minimal steps to reproduce |
| Expected Behavior | textarea | What should have happened |
| Actual Behavior | textarea | What actually happened (with tracebacks) |
| Package Version | input | Exact affected version |
| Python Version | input | To rule out incompatibilities |
| Operating System | dropdown | Linux/macOS/Windows |

### Feature Request (`feature_request.yml`)

| Field | Type | Purpose |
|-------|------|---------|
| Problem Statement | textarea | What problem does this feature solve? |
| Proposed Solution | textarea | The proposed solution |
| Alternatives Considered | textarea | Alternatives evaluated |
| Additional Context | textarea | References, screenshots, etc. |

### `config.yml`

```yaml
blank_issues_enabled: false       # ← Forbids issues without a template
```

This forces **all issues** to use a template. There is no way to open a blank issue.

---

## 4.5 SECURITY.md — Responsible Disclosure Policy

### What Is It?

`SECURITY.md` is a GitHub-recognized file that documents how to report security
vulnerabilities **privately**. GitHub automatically highlights it in the repository's
"Security" tab.

### Why Is It Mandatory?

Without a disclosure policy, a security researcher who discovers a vulnerability
has two options:

1. **Open a public issue** → Exposes the vulnerability to everyone before a fix
   exists.
2. **Don't report it** → The vulnerability persists indefinitely.

`SECURITY.md` offers a third path: a private channel for reporting and a commitment
to response timelines.

### Template Content

| Section | Purpose |
|---------|---------|
| **Supported Versions** | Which versions receive security patches |
| **Reporting a Vulnerability** | Private reporting route and triage expectations |
| **What to Include** | Information needed to assess the impact |
| **Response Timeline** | 48h for acknowledgment, 5 days for assessment, 90 days for fix |

---

## 4.6 Conventional Commits — Commit Message Format { #46-conventional-commits--commit-message-format }

### What Are They?

[Conventional Commits](https://www.conventionalcommits.org/) is a specification
for structuring commit messages (and, in this template, **PR titles**) with a
semantic prefix that communicates the intent and impact of the change.

### Message Anatomy

A Conventional Commit has up to three parts:

```
<type>[optional scope][!]: <description>
                                              ← blank line
[optional body]
                                              ← blank line
[optional footer(s)]
```

#### Part 1: Header (required)

The header is a single line, maximum 72 characters:

```
feat(auth): add JWT token refresh endpoint
│     │      │
│     │      └─ Description: imperative mood, lowercase, no period
│     └──────── Scope: affected module or component (optional)
└────────────── Type: semantic prefix (see table below)
```

#### Part 2: Body (optional)

The body provides additional context when the description alone is insufficient.
It is separated from the header by a blank line:

```
feat(auth): add JWT token refresh endpoint

The current implementation issues tokens with a fixed 1-hour expiration.
This change introduces a /auth/refresh endpoint that accepts a valid
refresh token and returns a new access token with a renewed expiry.

The refresh token rotation strategy follows RFC 6749 Section 6.
```

#### Part 3: Footer (optional)

Footers contain metadata. The most important is the `BREAKING CHANGE` footer:

```
feat(auth)!: replace session-based auth with JWT

BREAKING CHANGE: the /auth/login endpoint no longer returns a Set-Cookie
header. Clients must store the JWT token and send it via the
Authorization header.

Refs: #142, #198
```

### Standard Types

| Type | Meaning | SemVer Impact | Release Drafter Label |
|------|---------|---------------|----------------------|
| `feat` | New functionality | Minor (0.1.0 → 0.2.0) | `feature`, `enhancement` |
| `fix` | Bug fix | Patch (0.1.0 → 0.1.1) | `fix`, `bug` |
| `docs` | Documentation only | Patch | `docs`, `documentation` |
| `chore` | Maintenance (deps, CI, config) | Patch | `chore`, `refactor` |
| `refactor` | Code restructuring without functional change | Patch | `chore`, `refactor` |
| `perf` | Performance improvement | Patch | `performance`, `perf` |
| `test` | Adding or modifying tests | Patch | `chore` |
| `ci` | CI/CD configuration changes | Patch | `chore` |
| `build` | Build system or external dependencies | Patch | `chore` |
| `!` (suffix) | **Breaking change** (any type) | Major (0.x → 1.0.0) | `breaking`, `major` |

### Scope Usage

The scope is optional and indicates the module or component affected:

```
feat(parser): add support for nested YAML anchors
fix(cli): handle missing config file gracefully
refactor(db): extract connection pooling into dedicated module
chore(deps): bump pydantic to 2.10.6
```

Common scopes for this template: `auth`, `cli`, `api`, `db`, `deps`, `ci`, `docs`.

### Examples

#### Simple feature (no body needed)

```
feat: add invoice PDF export
```

#### Bug fix with context

```
fix(parser): prevent infinite loop on circular references

The recursive descent parser did not track visited nodes, causing a
stack overflow when the input contained circular $ref pointers.
Added a visited set to the traversal context.

Fixes: #231
```

#### Breaking change

```
feat(api)!: rename /users endpoint to /accounts

BREAKING CHANGE: all clients using the /users endpoint must update
their base URL to /accounts. The response schema remains unchanged.

Migration guide: https://docs.example.com/migration/v2
```

#### Dependency update

```
chore(deps): bump ruff from 0.14.0 to 0.15.8
```

### Relationship with Squash Merge

In this template, **only the PR title must follow Conventional Commits**. The
individual commits within a feature branch are discarded by squash merge and
do not need to follow any convention. The PR title becomes the single commit
message on `main`:

```
git log --oneline main

a1b2c3d feat: add invoice PDF export (#94)
e4f5g6h fix(parser): prevent infinite loop on circular references (#92)
i7j8k9l chore(deps): bump ruff from 0.14.0 to 0.15.8 (#91)
d0e1f2g feat(api)!: rename /users endpoint to /accounts (#89)
```

This produces a clean, machine-readable history that enables:

1. **Automatic changelogs** — Release Drafter reads PR titles and groups them
   by label (features, fixes, maintenance).
2. **Automatic version resolution** — The presence of `feat` → minor bump,
   `fix` → patch bump, `!` → major bump.
3. **Efficient debugging** — `git log --oneline --grep="feat"` filters all
   feature additions. `git log --oneline --grep="BREAKING"` finds all breaking
   changes.

---

## Pillar 4 Summary

| Element | File / Convention | Purpose |
|----------|-------------------|---------|
| **CODEOWNERS** | `.github/CODEOWNERS` | Algorithmic code ownership |
| **Trunk-Based Dev** | GitHub configuration | Linear history, squash merges |
| **Branch Naming** | `<type>/<description>` convention | Consistent, semantic branch names aligned with commit types |
| **Development Workflow** | Section 4.2 | Full lifecycle: branch → commit → push → PR → squash merge |
| **PR Template** | `.github/PULL_REQUEST_TEMPLATE.md` | Mandatory PR structure |
| **Issue Templates** | `.github/ISSUE_TEMPLATE/*.yml` | Structured forms for bugs/features |
| **SECURITY.md** | `SECURITY.md` | Private vulnerability disclosure channel |
| **Conventional Commits** | PR title convention | Semantic messages for changelogs, versioning, and debugging |
| **LICENSE** | `LICENSE` | Legal project protection |

[← Pillar 3: CI/CD](pillar-3-ci-cd.md) · [Next: Pillar 5 — Maintenance →](pillar-5-maintenance.md)
