import re
from typing import Annotated

from pydantic import AfterValidator, Field, StringConstraints

from multi_agent_sdlc.runtime.validation import (
    create_entry_point_validator,
    create_testing_dependency_validator,
    validate_application_arguments,
    validate_file_content,
    validate_project_relative_path,
)

MODULE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")

DEPENDENCY_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:\[[A-Za-z0-9._,-]+\])?"
    r"(?:(?:===|==|~=|!=|<=|>=|<|>)[A-Za-z0-9.*+!_-]+)?$"
)


PROHIBITED_TESTER_ENTRY_POINTS = {
    "pip",
    "pip3",
    "pipenv",
    "poetry",
    "bash",
    "sh",
    "zsh",
    "fish",
    "powershell",
    "pwsh",
    "twine",
    "docker",
    "kubectl",
    "terraform",
}


PROHIBITED_TESTER_DEPENDENCIES = {
    "pip",
    "uv",
    "virtualenv",
    "pipenv",
    "poetry",
    "twine",
}


PROHIBITED_TESTER_PYTHON_MODULES = {
    "pip",
    "ensurepip",
    "venv",
    "subprocess",
    "twine",
}


validate_tester_entry_point = create_entry_point_validator(
    role="Tester",
    prohibited_entry_points=PROHIBITED_TESTER_ENTRY_POINTS,
)

StandardInput = Annotated[
    str,
    Field(
        min_length=1,
        max_length=10_000,
        description=(
            "Text sent to the application's standard input. Separate "
            "interactive responses with newline characters. Omit this "
            "argument when no standard input is required."
        ),
    ),
]


EntryPoint = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=r"[A-Za-z0-9][A-Za-z0-9._-]*",
    ),
    AfterValidator(validate_tester_entry_point),
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

validate_module_name = create_entry_point_validator(
    role="Tester",
    prohibited_entry_points=PROHIBITED_TESTER_PYTHON_MODULES,
)

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

validate_testing_dependency = create_testing_dependency_validator(
    role="Tester", prohibited_tester_dependencies=PROHIBITED_TESTER_DEPENDENCIES
)

VerificationDependency = Annotated[
    str,
    AfterValidator(validate_testing_dependency),
]


VerificationDependencies = Annotated[
    list[VerificationDependency],
    Field(
        min_length=1,
        max_length=20,
        description="Verification dependencies to add with uv.",
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

from typing import TypedDict


class ProcessResult(TypedDict):
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool


class ProjectVerificationResult(TypedDict):
    verification_type: str
    passed: bool
    overall_exit_code: int
    checks: list[ProcessResult]


from pydantic import StringConstraints

NonBlankStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]
