from multi_agent_sdlc.runtime.validation import validate_file_content
from multi_agent_sdlc.runtime.validation import validate_project_relative_path
from multi_agent_sdlc.runtime.validation import create_testing_dependency_validator
from multi_agent_sdlc.runtime.validation import validate_application_arguments
from multi_agent_sdlc.runtime.validation import create_entry_point_validator
from typing import Annotated
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

PROHIBITED_TESTER_ENTRY_POINTS = {
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

PROHIBITED_TESTER_DEPENDENCIES = {
    "pytest",
    "pytest-cov",
    "coverage",
    "ruff",
    "mypy",
    "flake8",
    "tox",
    "nox",
}


validate_tester_entry_point = create_entry_point_validator(
    role="Tester",
    prohibited_entry_points=PROHIBITED_TESTER_ENTRY_POINTS,
)


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
    prohibited_entry_points=PROHIBITED_TESTER_ENTRY_POINTS,
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

TestingDependency = Annotated[
    str,
    AfterValidator(validate_testing_dependency),
]


TestingDependencies = Annotated[
    list[TestingDependency],
    Field(
        min_length=1,
        max_length=20,
        description="Testing dependencies to add with uv.",
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
