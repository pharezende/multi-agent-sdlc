

from multi_agent_sdlc.system.paths import normalise_relative_path

TEST_DIRECTORY_NAMES = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}

PROHIBITED_CODER_ENTRY_POINTS = {
    "pytest",
    "ruff",
    "mypy",
    "flake8",
    "coverage",
    "coverage3",
    "pip",
    "pip3",
    "bash",
    "sh",
    "zsh",
    "fish",
    "powershell",
    "pwsh",
}

PROHIBITED_CODER_PYTHON_MODULES = {
    "pytest",
    "unittest",
    "coverage",
    "pip",
    "ensurepip",
    "venv",
    "subprocess",
}

PROHIBITED_CODER_DEPENDENCY_PACKAGES = {
    "pytest",
    "pytest-cov",
    "tox",
    "nox",
}


def is_test_related_path(path: str) -> bool:
    """Return True when a path includes a blocked test directory."""
    candidate = normalise_relative_path(path)

    return any(part.lower() in TEST_DIRECTORY_NAMES for part in candidate.parts)


def reject_coder_test_path(path: str) -> None:
    """Prevent the Coder from writing into test-related directories."""
    if is_test_related_path(path):
        raise PermissionError(
            "The Coder cannot create or modify files or directories "
            f"inside test-related paths: {path}. "
            "Test implementation belongs to the Tester. "
            "Do not retry this operation using another tool or path."
        )
