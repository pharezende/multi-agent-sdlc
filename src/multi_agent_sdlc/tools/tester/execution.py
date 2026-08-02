from multi_agent_sdlc.tools.tester.descriptions import (
    TESTER_RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
from multi_agent_sdlc.tools.tester.validation import PythonModuleName
from multi_agent_sdlc.tools.tester.validation import ExecutionTimeout
from multi_agent_sdlc.tools.tester.validation import ApplicationArguments
from multi_agent_sdlc.tools.tester.validation import EntryPoint
from multi_agent_sdlc.tools.tester.descriptions import SYNC_PROJECT_DESCRIPTION
from multi_agent_sdlc.tools.tester.descriptions import RUN_PYTHON_MODULE_DESCRIPTION
from multi_agent_sdlc.tools.tester.descriptions import RUN_APPLICATION_DESCRIPTION
from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.state import DevState
from langchain.tools import ToolRuntime, tool


@tool(
    "tester_run_application",
    description=RUN_APPLICATION_DESCRIPTION,
)
def tester_run_application(
    entry_point: EntryPoint,
    runtime: ToolRuntime[DevState],
    arguments: ApplicationArguments | None = None,
    timeout_seconds: ExecutionTimeout = 15,
) -> dict[str, object]:

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            entry_point,
            *(arguments or []),
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "tester_run_python_module",
    description=RUN_PYTHON_MODULE_DESCRIPTION,
)
def tester_run_python_module(
    module: PythonModuleName,
    runtime: ToolRuntime[DevState],
    arguments: ApplicationArguments | None = None,
    stdin_text: str | None = None,
    timeout_seconds: ExecutionTimeout = 15,
) -> dict[str, object]:

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            "python",
            "-m",
            module,
            *(arguments or []),
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
        stdin_text=stdin_text,
    )


@tool(
    "tester_sync_project",
    description=SYNC_PROJECT_DESCRIPTION,
)
def tester_sync_project(
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> dict[str, object]:
    project_directory = get_project_directory(runtime)

    return execute_process(
        ["uv", "sync"],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


from typing import Annotated, Literal
from pydantic import Field

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


@tool(
    "tester_run_verification_command",
    description=TESTER_RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
def tester_run_verification_command(
    command: VerificationCommand,
    runtime: ToolRuntime[DevState],
    arguments: str | None = None,
    timeout_seconds: ExecutionTimeout = 120,
) -> dict[str, object]:
    project_directory = get_project_directory(runtime)

    return execute_process(
        ["uv", "run", command, *(arguments or [])],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
