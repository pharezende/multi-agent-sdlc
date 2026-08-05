from pathlib import Path

from langchain.tools import ToolRuntime, tool

from multi_agent_sdlc.runtime.paths import resolve_project_path
from multi_agent_sdlc.runtime.workspace import get_project_directory
from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.tools.coder.validation import ProjectRelativePath
from multi_agent_sdlc.tools.shared.description import (
    LIST_FILES_DESCRIPTION,
    READ_FILE_DESCRIPTION,
)


def get_directory_entries(
    directory: Path,
    project_directory: Path,
) -> list[str]:
    """Return sorted project-relative entries for one directory level."""

    entries: list[str] = []

    for item in sorted(
        directory.iterdir(),
        key=lambda candidate: (
            not candidate.is_dir(),
            candidate.name.casefold(),
        ),
    ):
        relative_path = item.relative_to(
            project_directory,
        ).as_posix()

        entries.append(f"{relative_path}/" if item.is_dir() else relative_path)

    return entries


@tool(
    "list_files",
    description=LIST_FILES_DESCRIPTION,
)
def list_files(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    target = resolve_project_path(project_directory, path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if target.is_file():
        return target.relative_to(
            project_directory,
        ).as_posix()

    entries = get_directory_entries(
        target,
        project_directory=project_directory,
    )

    return "\n".join(entries) or "(empty directory)"


@tool(
    "read_file",
    description=READ_FILE_DESCRIPTION,
)
def read_file(
    path: ProjectRelativePath,
    runtime: ToolRuntime[DevState],
) -> str:
    project_directory = get_project_directory(runtime)
    file_path = resolve_project_path(project_directory, path)

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"File is not valid UTF-8 text: {path}") from error
