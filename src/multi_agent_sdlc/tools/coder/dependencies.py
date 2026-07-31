from multi_agent_sdlc.tools.coder.validation import RuntimeDependencies
from multi_agent_sdlc.tools.coder.validation import ExecutionTimeout
from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.tools.coder.descriptions import (
    INSTALL_RUNTIME_DEPENDENCIES_DESCRIPTION,
)
from multi_agent_sdlc.state import DevState
from langchain.tools import ToolRuntime, tool


@tool(
    "install_runtime_dependencies",
    description=INSTALL_RUNTIME_DEPENDENCIES_DESCRIPTION,
)
def coder_install_runtime_dependencies(
    dependencies: RuntimeDependencies,
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> dict[str, object]:

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "add",
            *dependencies,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
