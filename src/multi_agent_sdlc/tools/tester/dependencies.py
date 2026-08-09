from multi_agent_sdlc.tools.tester.validation import ProcessResult
from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from workflow.state import DevState
from multi_agent_sdlc.tools.coder.validation import ExecutionTimeout
from multi_agent_sdlc.tools.tester.descriptions import (
    INSTALL_VERIFICATION_DEPENDENCIES_DESCRIPTION,
)
from multi_agent_sdlc.tools.tester.validation import VerificationDependencies


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
