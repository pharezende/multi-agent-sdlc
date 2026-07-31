from multi_agent_sdlc.tools.coder.validation import FileContent
from multi_agent_sdlc.tools.coder.validation import ProjectRelativePath
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.tools.coder.descriptions import (
    WRITE_FILE_DESCRIPTION,
    CREATE_DIRECTORY_DESCRIPTION,
)
from multi_agent_sdlc.runtime.paths import resolve_project_path
from multi_agent_sdlc.state import DevState
from langchain.tools import ToolRuntime, tool


@tool(
    "tester_write_file",
    description=WRITE_FILE_DESCRIPTION,
)
def tester_write_file(
    path: ProjectRelativePath,
    content: FileContent,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    file_path = resolve_project_path(project_directory, path)

    if file_path.exists() and file_path.is_dir():
        raise IsADirectoryError(f"Cannot replace a directory with a file: {path}")

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Written testing file: {path}"


@tool(
    "tester_create_directory",
    description=CREATE_DIRECTORY_DESCRIPTION,
)
def tester_create_directory(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    directory_path = resolve_project_path(
        project_directory,
        path,
    )

    if directory_path.exists() and not directory_path.is_dir():
        raise FileExistsError(f"A file already exists at this path: {path}")

    directory_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return f"Created testing directory: {path}"
