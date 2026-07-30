from __future__ import annotations

from pathlib import Path, PurePosixPath


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
    path: str,
) -> None:
    """Reject paths such as sandbox/project-name/src/file.py."""
    candidate = normalise_relative_path(path)
    parts = candidate.parts
    project_name = project_directory.name

    if len(parts) >= 2 and parts[0].lower() == "sandbox" and parts[1] == project_name:
        remaining_parts = parts[2:]

        suggested_path = (
            PurePosixPath(*remaining_parts).as_posix() if remaining_parts else "."
        )

        raise PermissionError(
            "Do not include the sandbox or project-directory prefix. "
            f"Use `{suggested_path}` instead of `{path}`."
        )


def resolve_project_path(
    project_directory: Path,
    path: str,
) -> Path:
    """Resolve a relative path and ensure it remains inside the project."""
    candidate = normalise_relative_path(path)

    reject_repeated_project_prefix(
        project_directory,
        path,
    )

    root = project_directory.resolve()
    resolved = (root / Path(*candidate.parts)).resolve()

    if not resolved.is_relative_to(root):
        raise PermissionError(f"Path escapes the project directory: {path}")

    return resolved
