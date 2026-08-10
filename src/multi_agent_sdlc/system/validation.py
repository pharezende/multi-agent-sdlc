from .paths import normalise_relative_path
from multi_agent_sdlc.tools.shared.validation import MODULE_PATTERN
from collections.abc import Callable

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name


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


def validate_project_relative_path(path: str) -> str:
    candidate = normalise_relative_path(path.strip())
    return candidate.as_posix()


def validate_file_content(content: str) -> str:
    if "\x00" in content:
        raise ValueError("File content cannot contain null bytes.")

    return content


def create_entry_point_validator(
    role: str,
    prohibited_entry_points: set[str],
) -> Callable[[str], str]:
    def validate_entry_point(entry_point: str) -> str:
        cleaned = entry_point.strip()

        if not cleaned:
            raise ValueError("Entry point cannot be empty.")

        if cleaned.casefold() in prohibited_entry_points:
            raise ValueError(f"The {role} cannot execute {cleaned}.")

        return cleaned

    return validate_entry_point


def create_module_name_validator(
    role: str,
    prohibited_python_modules: set[str],
) -> Callable[[str], str]:

    def validate_module_name(module: str) -> str:
        cleaned = module.strip()

        if not cleaned:
            raise ValueError("Module cannot be empty.")

        if not MODULE_PATTERN.fullmatch(cleaned):
            raise ValueError(f"Invalid Python module name: {cleaned}")

        root_module = cleaned.split(".", maxsplit=1)[0].lower()

        if root_module in prohibited_python_modules:
            raise PermissionError(f"The {role} cannot execute Python module {cleaned}.")

        return cleaned

    return validate_module_name


def create_dependency_validator(
    role: str,
    prohibited_dependencies: set[str],
) -> Callable[[str], str]:
    canonical_dependencies = set(
        canonicalize_name(name) for name in prohibited_dependencies
    )

    def validate_dependency(
        dependency: str,
    ) -> str:
        cleaned = dependency.strip()

        if not cleaned:
            raise ValueError("Dependency specification cannot be empty.")

        if cleaned.startswith("-"):
            raise PermissionError(
                "Dependency command-line options are not allowed: " f"{cleaned!r}."
            )

        requirement = parse_dependency(cleaned)

        if requirement.url is not None:
            raise PermissionError(
                "Git, URL, SSH, and local-file dependencies are not "
                f"allowed: {cleaned!r}."
            )

        dependency_name = canonicalize_name(requirement.name)

        if dependency_name in canonical_dependencies:
            raise PermissionError(f"The {role} cannot add dependency {cleaned!r}.")

        return cleaned

    return validate_dependency


def parse_dependency(
    specification: str,
) -> Requirement:
    """Parse a Python dependency specification."""

    try:
        return Requirement(specification)
    except InvalidRequirement as error:
        raise ValueError(
            f"Invalid dependency specification: {specification!r}."
        ) from error
