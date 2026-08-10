from typing import NotRequired
import re
from typing import Annotated

from pydantic import AfterValidator, Field, StringConstraints
from typing import TypedDict

from multi_agent_sdlc.runtime.validation import (
    create_entry_point_validator,
    create_dependency_validator,
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
