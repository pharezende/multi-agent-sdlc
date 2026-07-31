# This will require some refactoring in the future, e.g. moving some content to "centralized" files for code reuse.

from typing import Annotated
from multi_agent_sdlc.runtime.paths import normalise_relative_path
import re
from pydantic import AfterValidator, Field, StringConstraints

ENTRY_POINT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")

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


def validate_project_relative_path(path: str) -> str:
    candidate = normalise_relative_path(path.strip())
    return candidate.as_posix()


def normalise_dependency_name(specification: str) -> str:
    """Extract the normalised package name from a dependency specification."""
    match = re.match(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*",
        specification,
    )

    if match is None:
        return ""

    return match.group(0).lower().replace("_", "-")


def validate_file_content(content: str) -> str:
    if "\x00" in content:
        raise ValueError("File content cannot contain null bytes.")

    return content


EntryPoint = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=r"[A-Za-z0-9][A-Za-z0-9._-]*",
    ),
    AfterValidator(validate_entry_point),
]

ApplicationArguments = Annotated[
    list[str],
    Field(
        max_length=50,
        description="Arguments passed directly to the application.",
    ),
    AfterValidator(validate_application_arguments),
]

ExecutionTimeout = Annotated[
    int,
    Field(
        ge=1,
        le=200,
        description="Maximum application execution time in seconds.",
    ),
]

PythonModuleName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=200,
        description=(
            "A dotted Python module belonging to the generated application. "
            "Testing, package-management, environment-management, and "
            "process-execution modules are prohibited."
        ),
    ),
    AfterValidator(validate_module_name),
]

RuntimeDependency = Annotated[
    str,
    AfterValidator(validate_runtime_dependency),
]


RuntimeDependencies = Annotated[
    list[RuntimeDependency],
    Field(
        min_length=1,
        max_length=20,
        description="Runtime dependencies to add with uv.",
    ),
]

ProjectRelativePath = Annotated[
    str,
    Field(
        min_length=1,
        max_length=500,
        description=(
            "A path relative to the project directory. "
            "Absolute paths and parent-directory traversal are prohibited."
        ),
    ),
    AfterValidator(validate_project_relative_path),
]

FileContent = Annotated[
    str,
    Field(
        max_length=500_000,
        description="Complete UTF-8 text content to write to the file.",
    ),
    AfterValidator(validate_file_content),
]
