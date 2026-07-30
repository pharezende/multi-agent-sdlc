from multi_agent_sdlc.tools.coder.descriptions import (
    RUN_SYNC_PROJECT,
    RUN_PYTHON_MODULE_DESCRIPTION,
    RUN_APPLICATION_DESCRIPTION,
)
from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.tools.coder.validation import (
    validate_entry_point,
    validate_application_arguments,
    validate_module_name,
)
from multi_agent_sdlc.state import DevState
from langchain.tools import ToolRuntime, tool


@tool(
    "run_application",
    description=RUN_APPLICATION_DESCRIPTION,
)
def coder_run_application(
    entry_point: str,
    arguments: list[str],
    timeout_seconds: int,
    runtime: ToolRuntime,
) -> dict[str, object]:
    validated_entry_point = validate_entry_point(entry_point)
    validated_arguments = validate_application_arguments(arguments)

    if not 1 <= timeout_seconds <= 60:
        raise ValueError(f"timeout_seconds must be between 1 and {60}.")

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            validated_entry_point,
            *validated_arguments,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "run_python_module",
    description=RUN_PYTHON_MODULE_DESCRIPTION,
)
def coder_run_python_module(
    module: str,
    runtime: ToolRuntime[DevState],
    arguments: list[str] | None = None,
    timeout_seconds: int = 15,
) -> dict[str, object]:
    validated_module = validate_module_name(module)
    validated_arguments = validate_application_arguments(arguments or [])

    if not 1 <= timeout_seconds <= 60:
        raise ValueError(f"timeout_seconds must be between 1 and {60}.")

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "run",
            "python",
            "-m",
            validated_module,
            *validated_arguments,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )


@tool(
    "sync_project",
    description=RUN_SYNC_PROJECT,
)
def coder_sync_project(
    runtime: ToolRuntime[DevState],
    timeout_seconds: int = 120,
) -> dict[str, object]:
    project_directory = get_project_directory(runtime)

    return execute_process(
        ["uv", "sync"],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
