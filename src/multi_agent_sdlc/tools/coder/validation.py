from multi_agent_sdlc.runtime.paths import normalise_relative_path
from multi_agent_sdlc.tools.commands import normalise_dependency_name
import re


TEST_DIRECTORY_NAMES = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}

PROHIBITED_ENTRY_POINTS = {
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

PROHIBITED_PYTHON_MODULES = {
    "pytest",
    "unittest",
    "coverage",
    "pip",
    "ensurepip",
    "venv",
    "subprocess",
}

PROHIBITED_RUNTIME_PACKAGES = {
    "pytest",
    "pytest-cov",
    "coverage",
    "ruff",
    "mypy",
    "flake8",
    "tox",
    "nox",
}


def validate_entry_point(entry_point: str) -> str:
    """Validate and return a project entry-point name."""

    cleaned = entry_point.strip()

    if not cleaned:
        raise ValueError("Entry point cannot be empty.")

    if cleaned.lower() in PROHIBITED_ENTRY_POINTS:
        raise PermissionError(f"The Coder cannot execute `{cleaned}`.")

    if not ENTRY_POINT_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid application entry point: {cleaned}")

    return cleaned


ENTRY_POINT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

MODULE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")

DEPENDENCY_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:\[[A-Za-z0-9._,-]+\])?"
    r"(?:(?:===|==|~=|!=|<=|>=|<|>)[A-Za-z0-9.*+!_-]+)?$"
)

REMOTE_DEPENDENCY_PREFIXES = (
    "http://",
    "https://",
    "git+",
    "ssh://",
    "file:",
)


def validate_module_name(module: str) -> str:
    """Validate and return an application module name."""

    cleaned = module.strip()

    if not cleaned:
        raise ValueError("Module cannot be empty.")

    if not MODULE_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid Python module name: {cleaned}")

    root_module = cleaned.split(".", maxsplit=1)[0].lower()

    if root_module in PROHIBITED_PYTHON_MODULES:
        raise PermissionError(f"The Coder cannot execute Python module `{cleaned}`.")

    return cleaned


def validate_application_arguments(
    arguments: list[str],
) -> list[str]:
    """Validate arguments passed to an application or module."""

    validated: list[str] = []

    for argument in arguments:
        if not isinstance(argument, str):
            raise TypeError("Every application argument must be a string.")

        if "\n" in argument or "\r" in argument:
            raise PermissionError("Multiline application arguments are not allowed.")

        if "\x00" in argument:
            raise PermissionError(
                "Null bytes are not allowed in application arguments."
            )

        validated.append(argument)

    return validated


def validate_runtime_dependency(package: str) -> str:
    """Validate and return a runtime dependency specification."""
    cleaned = package.strip()

    if not cleaned:
        raise ValueError("Dependency specification cannot be empty.")

    lowered = cleaned.lower()

    if lowered.startswith(REMOTE_DEPENDENCY_PREFIXES):
        raise PermissionError(
            "Git, URL, SSH, and local-file dependencies are not allowed: " f"{cleaned}"
        )

    if cleaned.startswith("-"):
        raise PermissionError(
            f"Dependency command-line options are not allowed: {cleaned}"
        )

    if "@" in cleaned:
        raise PermissionError(
            f"Direct-reference dependencies are not allowed: {cleaned}"
        )

    if not DEPENDENCY_PATTERN.fullmatch(cleaned):
        raise ValueError(f"Invalid runtime dependency specification: {cleaned}")

    dependency_name = normalise_dependency_name(cleaned)

    if dependency_name in PROHIBITED_RUNTIME_PACKAGES:
        raise PermissionError(
            f"`{cleaned}` is a testing or development dependency. "
            "The Coder may add runtime dependencies only."
        )

    return cleaned


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
