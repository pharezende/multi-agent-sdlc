import shutil

from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.system.path_utils import resolve_project_path
from multi_agent_sdlc.tools.coder.descriptions import (
    CREATE_DIRECTORY_DESCRIPTION,
    DELETE_DIRECTORY_DESCRIPTION,
    DELETE_FILE_DESCRIPTION,
    MOVE_PATH_DESCRIPTION,
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


@tool(
    "move_path",
    description=MOVE_PATH_DESCRIPTION,
)
def coder_move_path(
    source_path: ProjectRelativePath,
    destination_path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(source_path)
    reject_coder_test_path(destination_path)

    project_directory = runtime.state["project_directory"]

    source = resolve_project_path(
        project_directory,
        source_path,
    )
    destination = resolve_project_path(
        project_directory,
        destination_path,
    )

    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    if destination.exists():
        raise FileExistsError(f"Destination path already exists: {destination_path}")

    if not destination.parent.is_dir():
        raise FileNotFoundError(
            f"Destination parent directory does not exist: {destination.parent}"
        )

    if source.is_dir() and source in destination.parents:
        raise ValueError("A directory cannot be moved inside itself.")

    source.rename(destination)

    return f"Moved production path: {source_path} " f"-> {destination_path}"


@tool(
    "delete_file",
    description=DELETE_FILE_DESCRIPTION,
)
def coder_delete_file(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = runtime.state["project_directory"]
    file_path = resolve_project_path(
        project_directory,
        path,
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Production file does not exist: {path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a production file: {path}")

    file_path.unlink()

    return f"Deleted production file: {path}"


@tool(
    "delete_directory",
    description=DELETE_DIRECTORY_DESCRIPTION,
)
def coder_delete_directory(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = runtime.state["project_directory"]
    directory_path = resolve_project_path(
        project_directory,
        path,
    )

    if directory_path == project_directory.resolve():
        raise PermissionError("The project root directory cannot be deleted.")

    if not directory_path.exists():
        raise FileNotFoundError(f"Production directory does not exist: {path}")

    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path is not a production directory: {path}")

    shutil.rmtree(directory_path)

    return f"Deleted production directory: {path}"
