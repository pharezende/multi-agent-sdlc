from pathlib import Path, PurePosixPath
from re import fullmatch

from multi_agent_sdlc.config import SANDBOX_ROOT


def normalise_relative_path(path: str) -> PurePosixPath:
    """Normalise and validate a project-relative path."""

    cleaned = path.strip().replace("\\", "/")

    if not cleaned:
        raise ValueError("Path cannot be empty.")

    candidate = PurePosixPath(cleaned)

    if candidate.is_absolute():
        raise PermissionError(f"Absolute paths are not allowed: {path}")

    if ".." in candidate.parts:
        raise PermissionError(f"Parent-directory traversal is not allowed: {path}")

    return candidate


def reject_repeated_project_prefix(
    project_directory: Path,
    candidate: PurePosixPath,
) -> None:
    """Reject paths prefixed with the current project directory."""
    parts = candidate.parts
    project_id = project_directory.name
    sandbox_root = project_directory.parent.name

    if parts and parts[0] == project_id:
        prefix_length = 1

    elif len(parts) >= 2 and parts[0] == sandbox_root and parts[1] == project_id:
        prefix_length = 2

    else:
        return

    remaining_parts = parts[prefix_length:]

    suggested_path = (
        PurePosixPath(*remaining_parts).as_posix() if remaining_parts else "."
    )

    raise PermissionError(
        "Do not include the project-directory prefix. "
        f"Use {suggested_path} instead of {candidate.as_posix()}."
    )


def resolve_project_path(
    project_directory: Path,
    path: str,
) -> Path:
    """Resolve a project-relative path and ensure it stays inside the project."""

    relative_path = normalise_relative_path(path)

    reject_repeated_project_prefix(
        project_directory,
        relative_path,
    )

    root = project_directory.resolve()
    resolved = (root / relative_path).resolve()

    if not resolved.is_relative_to(root):
        raise PermissionError(f"Path escapes the project directory: {path!r}")

    return resolved


def create_project_directory(project_id: str) -> Path:
    "Create project folder inside 'sandbox', e.g: terminal-calculator"

    if not fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("project_id must use lowercase kebab-case.")

    project_directory = Path(SANDBOX_ROOT) / project_id
    project_directory.mkdir(parents=True, exist_ok=True)

    return project_directory
