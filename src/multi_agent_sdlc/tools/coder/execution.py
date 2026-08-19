from multi_agent_sdlc.tools.coder.descriptions import (
    RUN_DOCKER_COMPOSE_EXEC_DESCRIPTION,
)
from multi_agent_sdlc.tools.coder.models import DockerComposeService
from multi_agent_sdlc.tools.coder.models import DockerComposeExecCommand
from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.process import execute_process
from multi_agent_sdlc.tools.coder.descriptions import (
    RUN_APPLICATION_DESCRIPTION,
    RUN_PYTHON_MODULE_DESCRIPTION,
    RUN_SYNC_PROJECT,
    RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
from multi_agent_sdlc.tools.coder.models import (
    EntryPoint,
    PythonModuleName,
    VerificationCommand,
)
from multi_agent_sdlc.tools.shared.models import (
    ApplicationArguments,
    ExecutionTimeout,
    ProcessResult,
    StandardInput,
)
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "run_application",
    description=RUN_APPLICATION_DESCRIPTION,
)
def coder_run_application(
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
    "run_python_module",
    description=RUN_PYTHON_MODULE_DESCRIPTION,
)
def coder_run_python_module(
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
    "sync_project",
    description=RUN_SYNC_PROJECT,
)
def coder_sync_project(
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
    "run_verification_command",
    description=RUN_VERIFICATION_COMMAND_DESCRIPTION,
)
def coder_run_verification_command(
    command: VerificationCommand,
    runtime: ToolRuntime[DevState],
    arguments: ApplicationArguments | None = None,
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:
    project_directory = runtime.state["project_directory"]

    return execute_process(
        ["uv", "run", command, *(arguments or [])],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "run_docker_compose_exec",
    description=RUN_DOCKER_COMPOSE_EXEC_DESCRIPTION,
)
def coder_run_docker_compose_exec(
    service: DockerComposeService,
    command: DockerComposeExecCommand,
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:
    project_directory = runtime.state["project_directory"]

    return execute_process(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            service,
            *command,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
