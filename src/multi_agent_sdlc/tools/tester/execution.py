from multi_agent_sdlc.tools.tester.descriptions import SYNC_PROJECT_DESCRIPTION
from multi_agent_sdlc.tools.tester.descriptions import RUN_PYTHON_MODULE_DESCRIPTION
from multi_agent_sdlc.tools.tester.descriptions import RUN_APPLICATION_DESCRIPTION
from multi_agent_sdlc.tools.coder.validation import PythonModuleName
from multi_agent_sdlc.tools.coder.validation import ExecutionTimeout
from multi_agent_sdlc.tools.coder.validation import ApplicationArguments
from multi_agent_sdlc.tools.coder.validation import EntryPoint
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
