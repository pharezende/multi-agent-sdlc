from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.paths import resolve_project_path
from multi_agent_sdlc.tools.coder.descriptions import (
    CREATE_DIRECTORY_DESCRIPTION,
    WRITE_FILE_DESCRIPTION,
)
from multi_agent_sdlc.tools.coder.validation import (
    reject_coder_test_path,
)
from multi_agent_sdlc.tools.shared.models import FileContent, ProjectRelativePath
from multi_agent_sdlc.workflow.state import DevState


@tool(
    "write_file",
    description=WRITE_FILE_DESCRIPTION,
)
def coder_write_file(
    path: ProjectRelativePath,
    content: FileContent,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = runtime.state["project_directory"]
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

    return f"Written production file: {path}"


@tool(
    "create_directory",
    description=CREATE_DIRECTORY_DESCRIPTION,
)
def coder_create_directory(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = runtime.state["project_directory"]
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

    return f"Created production directory: {path}"
