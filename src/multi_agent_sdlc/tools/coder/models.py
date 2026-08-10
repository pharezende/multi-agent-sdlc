from multi_agent_sdlc.tools.shared.validation import create_dependency_validator
from multi_agent_sdlc.tools.shared.validation import create_module_name_validator
from multi_agent_sdlc.tools.shared.validation import create_entry_point_validator
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, StringConstraints


from multi_agent_sdlc.tools.coder.validation import (
    PROHIBITED_CODER_DEPENDENCY_PACKAGES,
    PROHIBITED_CODER_ENTRY_POINTS,
    PROHIBITED_CODER_PYTHON_MODULES,
)

validate_entry_point = create_entry_point_validator(
    role="Coder",
    prohibited_entry_points=PROHIBITED_CODER_ENTRY_POINTS,
)

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

validate_module_name = create_module_name_validator(
    role="Coder", prohibited_python_modules=PROHIBITED_CODER_PYTHON_MODULES
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

validate_dependency = create_dependency_validator(
    role="Coder", prohibited_dependencies=PROHIBITED_CODER_DEPENDENCY_PACKAGES
)

PackageDependency = Annotated[
    str,
    AfterValidator(validate_dependency),
]


PackageDependencyList = Annotated[
    list[PackageDependency],
    Field(
        min_length=1,
        max_length=20,
        description="Package Dependencies to add with uv.",
    ),
]

VerificationCommand = Annotated[
    Literal[
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
