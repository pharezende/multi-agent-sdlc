from multi_agent_sdlc.tools.tester.verification import _build_mypy_command
import json

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from multi_agent_sdlc.system.process import execute_process
from multi_agent_sdlc.tools.shared.models import (
    ApplicationArguments,
    ExecutionTimeout,
    ProcessResult,
    StandardInput,
)
from multi_agent_sdlc.tools.tester.descriptions import (
    RUN_APPLICATION_DESCRIPTION,
    RUN_PYTHON_MODULE_DESCRIPTION,
    SYNC_PROJECT_DESCRIPTION,
    TESTER_RUN_BUILD_DESCRIPTION,
    TESTER_RUN_PROJECT_VERIFICATION_DESCRIPTION,
    TESTER_RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
from multi_agent_sdlc.tools.tester.model import (
    EntryPoint,
    ProjectVerificationResult,
    PythonModuleName,
    VerificationCommand,
)
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "tester_run_application",
    description=RUN_APPLICATION_DESCRIPTION,
)
def tester_run_application(
    entry_point: EntryPoint,
    runtime: ToolRuntime[DevState],
    arguments: ApplicationArguments | None = None,
    stdin_text: StandardInput | None = None,
    timeout_seconds: ExecutionTimeout = 15,
) -> ProcessResult:

    project_directory = runtime.state["project_directory"]

    return execute_process(
        [
            "uv",
            "run",
            entry_point,
            *(arguments or []),
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
        stdin_text=stdin_text,
    )


@tool(
    "tester_run_python_module",
    description=RUN_PYTHON_MODULE_DESCRIPTION,
)
def tester_run_python_module(
    module: PythonModuleName,
    runtime: ToolRuntime[DevState],
    arguments: ApplicationArguments | None = None,
    stdin_text: StandardInput | None = None,
    timeout_seconds: ExecutionTimeout = 15,
) -> ProcessResult:

    project_directory = runtime.state["project_directory"]

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
) -> ProcessResult:
    project_directory = runtime.state["project_directory"]

    return execute_process(
        ["uv", "sync"],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "tester_run_build",
    description=TESTER_RUN_BUILD_DESCRIPTION,
)
def tester_run_build(
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:
    """Build the project distributions using uv."""

    project_directory = runtime.state["project_directory"]

    return execute_process(
        command=["uv", "build"],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "tester_run_verification_command",
    description=TESTER_RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
def tester_run_verification_command(
    command: VerificationCommand,
    runtime: ToolRuntime[DevState],
    arguments: list[str] | None = None,
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:
    project_directory = runtime.state["project_directory"]

    return execute_process(
        [
            "uv",
            "run",
            command,
            *(arguments or []),
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "tester_run_project_verification",
    description=TESTER_RUN_PROJECT_VERIFICATION_DESCRIPTION,
)
def tester_run_project_verification(
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 200,
) -> Command:
    project_directory = runtime.state["project_directory"]

    commands = [
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "ruff", "format", "--check", "."],
        _build_mypy_command(project_directory),
        ["uv", "run", "pytest"],
    ]

    checks = [
        execute_process(
            command=command,
            project_directory=project_directory,
            timeout_seconds=timeout_seconds,
        )
        for command in commands
    ]

    passed = all(not check["timed_out"] and check["exit_code"] == 0 for check in checks)

    result: ProjectVerificationResult = {
        "verification_type": "complete_project_verification",
        "passed": passed,
        "overall_exit_code": 0 if passed else 1,
        "checks": checks,
    }

    return Command(
        update={
            "current_project_verification_result": result,
            "tester_messages": [
                ToolMessage(
                    content=json.dumps(result),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
