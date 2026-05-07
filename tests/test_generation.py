import shutil
import subprocess
from pathlib import Path

# =============================================================================
# Python Project Template — Template Testing Suite
# Tests move from .jinja into rendered Python/TOML/Markdown
# =============================================================================


def run_command(project_path: Path, *command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=project_path,
        capture_output=True,
        text=True,
        check=False,
    )


def assert_command_ok(result: subprocess.CompletedProcess[str], context: str) -> None:
    assert result.returncode == 0, (
        f"{context} failed with exit code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def initialize_git_repo(project_path: Path) -> None:
    init_result = run_command(project_path, "git", "init")
    assert_command_ok(init_result, "Git repository initialization")


def sync_project(project_path: Path, *, include_docs: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["uv", "sync", "--dev"]
    if include_docs:
        command.extend(["--group", "docs"])
    return run_command(project_path, *command)


def run_ruff(project_path: Path) -> subprocess.CompletedProcess[str]:
    """Smoke test: check if the rendered project is lint-free (Ruff)."""
    return run_command(project_path, "uv", "run", "ruff", "check", ".")


def run_pyright(project_path: Path) -> subprocess.CompletedProcess[str]:
    """Smoke test: check if the rendered project is type-safe (Pyright)."""
    return run_command(project_path, "uv", "run", "pyright")


def run_pytest(project_path: Path) -> subprocess.CompletedProcess[str]:
    return run_command(project_path, "uv", "run", "pytest", "--cov=src")


def build_package(project_path: Path) -> subprocess.CompletedProcess[str]:
    return run_command(project_path, "uv", "build")


def build_docs(project_path: Path) -> subprocess.CompletedProcess[str]:
    return run_command(project_path, "uv", "run", "mkdocs", "build", "--strict")


def run_import_smoke(project_path: Path, package_name: str) -> subprocess.CompletedProcess[str]:
    return run_command(
        project_path,
        "uv",
        "run",
        "python",
        "-c",
        f"from {package_name} import greet; print(greet('Smoke'))",
    )

# -----------------------------------------------------------------------------
# Test Scenario 1: Standard Elite (The full package)
# -----------------------------------------------------------------------------

def test_standard_generation(copie):
    """Verify that 'Standard' mode generates all components."""
    result = copie.copy(extra_answers={
        "config_wizard": "Standard Elite 2026 (Recommended)",
        "project_name": "test-standard",
        "github_org": "test-org",
        "author_name": "Test Author",
        "author_email": "test@example.com",
    })
    
    assert result.exit_code == 0
    assert result.exception is None
    
    # Structural checks (Presence)
    assert (result.project_dir / ".github" / "workflows" / "ci.yml").exists()
    assert (result.project_dir / "docs" / "index.md").exists()
    assert (result.project_dir / "tests").is_dir()
    assert (result.project_dir / "pyproject.toml").exists()
    assert (result.project_dir / "README.md").exists()
    assert (result.project_dir / ".pre-commit-config.yaml").exists()
    assert (result.project_dir / "renovate.json").exists()
    assert not (result.project_dir / "tests" / "__pycache__").exists()

    initialize_git_repo(result.project_dir)

    sync_result = sync_project(result.project_dir, include_docs=True)
    assert_command_ok(sync_result, "uv sync for standard project")

    lint_result = run_ruff(result.project_dir)
    assert_command_ok(lint_result, "Ruff in standard project")

    type_result = run_pyright(result.project_dir)
    assert_command_ok(type_result, "Pyright in standard project")

    test_result = run_pytest(result.project_dir)
    assert_command_ok(test_result, "Pytest in standard project")

    build_result = build_package(result.project_dir)
    assert_command_ok(build_result, "Package build in standard project")

    smoke_result = run_import_smoke(result.project_dir, "test_standard")
    assert_command_ok(smoke_result, "Import smoke test in standard project")
    assert smoke_result.stdout.strip() == "Hello, Smoke!"

    docs_result = build_docs(result.project_dir)
    assert_command_ok(docs_result, "MkDocs build in standard project")

# -----------------------------------------------------------------------------
# Test Scenario 2: Minimal Custom (No GitHub, No Docs, No Tests)
# -----------------------------------------------------------------------------

def test_minimal_generation(copie):
    """Verify that 'Custom' mode with all features disabled only leaves essentials."""
    result = copie.copy(extra_answers={
        "config_wizard": "Custom Selection (Granular control)",
        "include_github": False,
        "include_docs": False,
        "include_tests": False,
        "include_pre_commit": False,
        "project_name": "test-minimal",
        "author_name": "Test Author",
        "author_email": "test@example.com",
    })
    
    assert result.exit_code == 0
    
    # Removal checks (Physical cleanup)
    assert not (result.project_dir / ".github").exists()
    assert not (result.project_dir / "docs").exists()
    assert not (result.project_dir / "tests").exists()
    assert not (result.project_dir / ".pre-commit-config.yaml").exists()
    assert not (result.project_dir / "renovate.json").exists()
    
    # Content checks (Jinja conditioning in pyproject.toml)
    pyproject_content = (result.project_dir / "pyproject.toml").read_text()
    assert "github.com" not in pyproject_content
    assert "dependency-groups.docs" not in pyproject_content
    assert "pytest" not in pyproject_content # Should not be in dev group

    initialize_git_repo(result.project_dir)

    sync_result = sync_project(result.project_dir)
    assert_command_ok(sync_result, "uv sync for minimal project")

    lint_result = run_ruff(result.project_dir)
    assert_command_ok(lint_result, "Ruff in minimal project")

    type_result = run_pyright(result.project_dir)
    assert_command_ok(type_result, "Pyright in minimal project")

    build_result = build_package(result.project_dir)
    assert_command_ok(build_result, "Package build in minimal project")

    smoke_result = run_import_smoke(result.project_dir, "test_minimal")
    assert_command_ok(smoke_result, "Import smoke test in minimal project")
    assert smoke_result.stdout.strip() == "Hello, Smoke!"


def test_generation_without_python_on_path(copie, monkeypatch, tmp_path):
    """Verify cleanup works even when no python executable is available on PATH."""
    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()

    git_path = shutil.which("git")
    assert git_path is not None
    (empty_bin / "git").symlink_to(git_path)

    monkeypatch.setenv("PATH", str(empty_bin))

    result = copie.copy(extra_answers={
        "config_wizard": "Custom Selection (Granular control)",
        "include_github": False,
        "include_docs": False,
        "include_tests": False,
        "include_pre_commit": False,
        "project_name": "test-no-python-path",
        "author_name": "Test Author",
        "author_email": "test@example.com",
    })

    assert result.exit_code == 0
    assert result.exception is None
    assert not (result.project_dir / ".github").exists()
    assert not (result.project_dir / "docs").exists()
    assert not (result.project_dir / "tests").exists()
    assert not (result.project_dir / ".pre-commit-config.yaml").exists()
    assert not (result.project_dir / "renovate.json").exists()
    assert not (result.project_dir / ".copier-cleanup.py").exists()

# -----------------------------------------------------------------------------
# Test Scenario 3: GitHub Only (Hybrid)
# -----------------------------------------------------------------------------

def test_github_no_docs(copie):
    """Verify that 'Custom' mode can include GitHub but exclude Docs."""
    result = copie.copy(extra_answers={
        "config_wizard": "Custom Selection (Granular control)",
        "include_github": True,
        "include_docs": False,
        "include_ci": True,
        "project_name": "test-hybrid",
        "github_org": "test-org",
        "author_name": "Test Author",
        "author_email": "test@example.com",
    })
    
    assert result.exit_code == 0
    
    # Correct folder separation
    assert (result.project_dir / ".github").exists()
    assert not (result.project_dir / "docs").exists()
    assert not (result.project_dir / "mkdocs.yml").exists()
    
    # Content checks in README
    readme_content = (result.project_dir / "README.md").read_text()
    assert "[![CI]" in readme_content # Badge should exist
    assert "MkDocs" not in readme_content # Docs reference should NOT exist

    initialize_git_repo(result.project_dir)

    sync_result = sync_project(result.project_dir)
    assert_command_ok(sync_result, "uv sync for hybrid project")

    lint_result = run_ruff(result.project_dir)
    assert_command_ok(lint_result, "Ruff in hybrid project")

    type_result = run_pyright(result.project_dir)
    assert_command_ok(type_result, "Pyright in hybrid project")
