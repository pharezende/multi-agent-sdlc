from multi_agent_sdlc.tools.tester.validation import TestingDependencies
from multi_agent_sdlc.tools.coder.validation import ExecutionTimeout
from multi_agent_sdlc.runtime.process import execute_process
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.state import DevState
from langchain.tools import ToolRuntime, tool


@tool(
    "install_testing_dependencies",
    description=INSTALL_TESTING_DEPENDENCIES_DESCRIPTION,
)
def tester_install_testing_dependencies(
    dependencies: TestingDependencies,
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
