from multi_agent_sdlc.system.path_utils import normalise_relative_path

TEST_FILE_PREFIXES = {
    "test_",
}

TEST_FILE_SUFFIXES = {
    "_test.py",
}

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
    """Return True when a path refers to test-owned content."""
    candidate = normalise_relative_path(path)

    if any(part.lower() in TEST_DIRECTORY_NAMES for part in candidate.parts):
        return True

    filename = candidate.name.lower()

    return (
        filename.startswith(tuple(TEST_FILE_PREFIXES))
        or filename.endswith(tuple(TEST_FILE_SUFFIXES))
        or "_test_" in filename
    )


def reject_coder_test_path(path: str) -> None:
    """Prevent the Coder from writing into test-related directories."""
    if is_test_related_path(path):
        raise PermissionError(
            "The Coder cannot create or modify files or directories "
            f"inside test-related paths: {path}. "
            "Test implementation belongs to the Tester. "
            "Do not retry this operation using another tool or path."
        )
