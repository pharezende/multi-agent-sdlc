from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.process import execute_process
from multi_agent_sdlc.tools.coder.descriptions import (
    INSTALL_PACKAGE_DEPENDENCIES_DESCRIPTION,
)
from multi_agent_sdlc.tools.coder.models import PackageDependencyList
from multi_agent_sdlc.tools.shared.models import ExecutionTimeout, ProcessResult
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "install_package_dependencies",
    description=INSTALL_PACKAGE_DEPENDENCIES_DESCRIPTION,
)
def coder_install_package_dependencies(
    dependencies: PackageDependencyList,
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:

    project_directory = runtime.state["project_directory"]

    return execute_process(
        [
            "uv",
            "add",
            *dependencies,
        ],
        project_directory=project_directory,
        timeout_seconds=timeout_seconds,
    )
