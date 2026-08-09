from multi_agent_sdlc.workflow.state import DevState
from pathlib import Path

from langchain.tools import ToolRuntime


def get_project_directory(
    runtime: ToolRuntime[DevState],
) -> Path:
    """Return the absolute project root stored in the graph state."""
    project_directory = runtime.state.get("project_directory")

    if not project_directory:
        raise RuntimeError("`project_directory` is missing from the graph state.")

    root = Path(project_directory).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Project directory does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    return root
