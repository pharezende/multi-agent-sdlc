from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.system.validation import create_module_name_validator
from multi_agent_sdlc.tools.tester.validation import PROHIBITED_TESTER_DEPENDENCIES
from multi_agent_sdlc.tools.tester.validation import PROHIBITED_TESTER_PYTHON_MODULES
from multi_agent_sdlc.tools.tester.validation import PROHIBITED_TESTER_ENTRY_POINTS
from typing import NotRequired
import re
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, StringConstraints
from typing import TypedDict

from multi_agent_sdlc.system.validation import (
    create_entry_point_validator,
    create_dependency_validator,
)

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

validate_module_name = create_module_name_validator(
    role="Tester",
    prohibited_python_modules=PROHIBITED_TESTER_PYTHON_MODULES,
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

validate_testing_dependency = create_dependency_validator(
    role="Tester", prohibited_dependencies=PROHIBITED_TESTER_DEPENDENCIES
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


class ProjectVerificationResult(TypedDict):
    verification_type: str
    passed: bool
    overall_exit_code: int
    checks: list[ProcessResult]


VerificationCommand = Annotated[
    Literal[
        "pytest",
        "ruff",
        "mypy",
        "coverage",
    ],
    Field(
        description=(
            "Approved development or verification executable to run "
            "inside the project's uv-managed environment."
        )
    ),
]
