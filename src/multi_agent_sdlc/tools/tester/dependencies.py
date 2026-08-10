from multi_agent_sdlc.tools.shared.models import ProcessResult
from multi_agent_sdlc.tools.tester.model import VerificationDependencies
from multi_agent_sdlc.tools.tester.descriptions import (
    INSTALL_VERIFICATION_DEPENDENCIES_DESCRIPTION,
)
from multi_agent_sdlc.tools.shared.models import ExecutionTimeout
from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.process import execute_process
from multi_agent_sdlc.system.workspace import get_project_directory
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "tester_install_verification_dependencies",
    description=INSTALL_VERIFICATION_DEPENDENCIES_DESCRIPTION,
)
def tester_install_verification_dependencies(
    dependencies: VerificationDependencies,
    runtime: ToolRuntime[DevState],
    timeout_seconds: ExecutionTimeout = 120,
) -> ProcessResult:

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
