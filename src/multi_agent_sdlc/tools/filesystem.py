from multi_agent_sdlc.state import DevState
from langgraph.prebuilt import ToolRuntime
from multi_agent_sdlc.tools.path_validation import resolve_project_path
from pathlib import Path

from langchain_core.tools import tool


@tool
def read_file(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    """Read a UTF-8 file inside the current project."""

    project_directory = get_project_directory(runtime)

    file_path = resolve_project_path(
        project_directory,
        path,
    )

    if not file_path.is_file():
        raise FileNotFoundError(path)

    return file_path.read_text(encoding="utf-8")


@tool
def write_file(
    path: str,
    content: str,
    runtime: ToolRuntime[DevState],
) -> str:
    """Create or replace a UTF-8 file inside the current project."""

    project_directory = get_project_directory(runtime)

    file_path = resolve_project_path(
        project_directory=project_directory,
        relative_path=path,
    )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Written file: {path}"


@tool
def list_files(
    runtime: ToolRuntime[DevState],
    path: str = ".",
) -> list[str]:
    """List files recursively inside the current project."""

    project_directory = get_project_directory(runtime)

    directory = resolve_project_path(
        project_directory=project_directory,
        relative_path=path,
    )

    if not directory.is_dir():
        raise NotADirectoryError(f"Directory does not exist: {path}")

    project_root = project_directory.resolve()

    return sorted(
        str(file.relative_to(project_root))
        for file in directory.rglob("*")
        if file.is_file()
    )


@tool
def create_directory(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    """Create a directory inside the current project."""

    project_directory = get_project_directory(runtime)

    directory = resolve_project_path(
        project_directory=project_directory,
        relative_path=path,
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return f"Created directory: {path}"


def get_project_directory(
    runtime: ToolRuntime[DevState],
) -> Path:
    """Retrieve project directory"""

    project_directory = runtime.state.get("project_directory")

    if not project_directory:
        raise ValueError("project_directory is missing from the graph state.")

    directory = Path(project_directory)

    if not directory.is_dir():
        raise NotADirectoryError(f"Project directory does not exist: {directory}")

    return directory.resolve()
