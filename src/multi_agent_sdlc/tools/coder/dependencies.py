from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.tools.coder.validation import validate_runtime_dependency
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
    packages: list[str],
    runtime: ToolRuntime[DevState],
    timeout_seconds: int = 120,
) -> dict[str, object]:
    if not packages:
        raise ValueError("At least one runtime dependency is required.")

    validated_packages = [validate_runtime_dependency(package) for package in packages]

    if not 1 <= timeout_seconds <= 180:
        raise ValueError(f"timeout_seconds must be between 1 and {180}.")

    project_directory = get_project_directory(runtime)

    return execute_process(
        [
            "uv",
            "add",
            *validated_packages,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
